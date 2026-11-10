from decimal import Decimal

from django.db import models
from django.db.models import Min, Max, Sum
from django.core.exceptions import ValidationError
from django.utils import timezone

from mainsite.models import Organization
from people.models import Employee


class Role(models.Model):
    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="submission_roles"
    )
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=300, blank=True)
    members = models.ManyToManyField(
        "people.Employee", related_name="submission_roles", blank=True
    )


class MileageSubmission(models.Model):
    class Meta:
        ordering = ["-pk"]

    reimbursement_rate = models.DecimalField(
        max_digits=6, decimal_places=3
    )
    submission = models.OneToOneField(
        "Submission",
        on_delete=models.CASCADE,
        related_name="mileage_submission",
    )

    @property
    def total_miles(self):
        total = self.rows.aggregate(total=Sum("miles"))["total"]
        return total or 0

    @property
    def travel_dates(self):
        dates = self.rows.aggregate(
            start=Min("date"),
            end=Max("date")
        )
        if dates["start"] and dates["end"]:
            return f"{dates['start']} - {dates['end']}"
        return "" 

    @property
    def total_reimbursement(self):
        return Decimal(self.total_miles) * self.reimbursement_rate


class MileageSubmissionRow(models.Model):
    class Meta:
        ordering = ["row_order", "pk"]

    mileage_submission = models.ForeignKey(
        MileageSubmission,
        on_delete=models.CASCADE,
        related_name="rows",
    )
    row_order = models.PositiveIntegerField(default=0)
    date = models.DateField()
    purpose = models.CharField(max_length=255)
    contract_fund = models.CharField(max_length=255)
    odometer_start = models.PositiveIntegerField()
    odometer_finish = models.PositiveIntegerField()
    miles = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if self.odometer_finish < self.odometer_start:
            raise ValidationError(
                "Odometer finish cannot be less than odometer start."
            )
        self.miles = self.odometer_finish - self.odometer_start
        super().save(*args, **kwargs)


class Submission(models.Model):
    FORM_TYPE_MILEAGE = "mileage"
    FORM_TYPE_CHOICES = (
        (FORM_TYPE_MILEAGE, "Mileage Reimbursement"),
    )

    STATUS_SUBMITTED = "submitted"
    STATUS_APPROVED = "approved"
    STATUS_CHOICES = (
        (STATUS_SUBMITTED, "Submitted"),
        (STATUS_APPROVED, "Approved"),
    )

    class Meta:
        ordering = ["-created_at", "-pk"]

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="submissions"
    )
    submitter = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="submissions"
    )
    form_type = models.CharField(max_length=50, choices=FORM_TYPE_CHOICES)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_SUBMITTED
    )
    approver_role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="submissions",
    )
    approved_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="approved_submissions",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(blank=True, null=True)

    def can_edit(self, employee):
        return (
            employee
            and self.status != self.STATUS_APPROVED
            and self.submitter_id == employee.pk
        )

    def approve(self, approver):
        self.status = self.STATUS_APPROVED
        self.approved_by = approver
        self.approved_at = timezone.now()
        self.save()
