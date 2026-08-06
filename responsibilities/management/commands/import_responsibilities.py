import csv

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify

from mainsite.models import Organization
from people.models import Employee
from responsibilities.models import Responsibility, Tag


class Command(BaseCommand):
	help = "Import responsibilities from a CSV file for an organization."

	def add_arguments(self, parser):
		parser.add_argument(
			"organization_name",
			type=str,
			help="Name of the organization to import responsibilities for.",
		)
		parser.add_argument(
			"csv_file",
			type=str,
			help="Path to CSV file with responsibilities data.",
		)

	def _parse_name(self, full_name):
		full_name = (full_name or "").strip()
		if not full_name:
			return "", ""
		name_parts = full_name.split()
		first_name = name_parts[0]
		last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
		return first_name, last_name

	def _generate_unique_username(self, organization, first_name, last_name):
		base = slugify(
			f"{organization.name}-{first_name}-{last_name}"
		).replace("-", "_")
		if not base:
			base = "employee"

		username = base
		suffix = 2
		while User.objects.filter(username=username).exists():
			username = f"{base}_{suffix}"
			suffix += 1
		return username

	def _get_or_create_employee_from_name(self, organization, full_name):
		first_name, last_name = self._parse_name(full_name)
		if not first_name:
			return None, False

		existing_employee = Employee.objects.filter(
			organization=organization,
			user__first_name__iexact=first_name,
			user__last_name__iexact=last_name,
		).select_related("user").first()
		if existing_employee:
			return existing_employee, False

		candidate_user = User.objects.filter(
			first_name__iexact=first_name,
			last_name__iexact=last_name,
		).first()

		if candidate_user and not hasattr(candidate_user, "employee"):
			user = candidate_user
			user_created = False
		else:
			username = self._generate_unique_username(
				organization,
				first_name,
				last_name,
			)
			user = User.objects.create(
				username=username,
				first_name=first_name,
				last_name=last_name,
			)
			user_created = True

		employee, employee_created = Employee.objects.get_or_create(
			user=user,
			defaults={
				"organization": organization,
				"active": True,
			},
		)
		if not employee.organization:
			employee.organization = organization
			employee.save(update_fields=["organization"])
		return employee, (user_created or employee_created)

	def handle(self, *args, **options):
		organization_name = options["organization_name"].strip()
		csv_file_path = options["csv_file"]

		try:
			organization = Organization.objects.get(name=organization_name)
		except Organization.DoesNotExist:
			raise CommandError(
				f"Organization '{organization_name}' does not exist."
			)

		created_responsibilities = 0
		created_tags = 0
		created_people = 0

		try:
			with open(csv_file_path, "r", encoding="latin-1", newline="") as f:
				reader = csv.reader(f)

				with transaction.atomic():
					for row_number, row in enumerate(reader, start=1):
						if not row or not any(cell.strip() for cell in row):
							continue

						# Skip common header rows.
						if row_number == 1 and row[0].strip().lower() in {
							"responsibilityname",
							"name",
						}:
							continue

						padded = row + [""] * (6 - len(row))
						name = padded[0].strip()
						description = padded[1].strip()
						link = padded[2].strip()
						tags_raw = padded[3].strip()
						primary_name = padded[4].strip()
						secondary_name = padded[5].strip()

						if not name:
							self.stdout.write(self.style.WARNING(
								f"Skipping row {row_number}: missing responsibility name."
							))
							continue

						primary_employee, primary_created = \
							self._get_or_create_employee_from_name(
								organization, primary_name
							)
						secondary_employee, secondary_created = \
							self._get_or_create_employee_from_name(
								organization, secondary_name
							)

						if primary_created:
							created_people += 1
						if secondary_created:
							created_people += 1

						responsibility, responsibility_created = Responsibility.objects.get_or_create(
							organization=organization,
							name=name,
							description=description,
							link=link,
							primary_employee=primary_employee,
							secondary_employee=secondary_employee,
						)
						if responsibility_created:
							created_responsibilities += 1

						if tags_raw:
							for tag_name in [
								part.strip() for part in tags_raw.split("|")
								if part.strip()
							]:
								tag, tag_created = Tag.objects.get_or_create(
									organization=organization,
									name=tag_name,
								)
								if tag_created:
									created_tags += 1
								responsibility.tags.add(tag)

		except FileNotFoundError:
			raise CommandError(f"File '{csv_file_path}' does not exist.")
		except OSError as exc:
			raise CommandError(f"Unable to read file '{csv_file_path}': {exc}")

		self.stdout.write(self.style.SUCCESS(
			"Import complete: "
			f"{created_responsibilities} responsibilities, "
			f"{created_tags} new tags, "
			f"{created_people} created/linked employees."
		))
