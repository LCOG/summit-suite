from decimal import Decimal

from django.db import models
from django.db.models import Q, Sum
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

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="mileage_submissions",
    )
    submitter = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="mileage_submissions",
    )
    certification_statement = models.TextField(blank=True)
    reimbursement_rate = models.DecimalField(
        max_digits=6, decimal_places=3, default=Decimal("0.585")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_miles(self):
        total = self.rows.aggregate(total=Sum("miles"))["total"]
        return total or 0

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
        ordering = ["-submitted_at", "-pk"]
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(form_type="mileage", mileage_submission__isnull=False)
                    | ~Q(form_type="mileage")
                ),
                name="submission_requires_mileage_when_mileage_type",
            ),
            models.UniqueConstraint(
                fields=["mileage_submission"],
                condition=Q(form_type="mileage"),
                name="unique_submission_per_mileage_submission",
            ),
        ]

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
    submitted_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    mileage_submission = models.ForeignKey(
        MileageSubmission,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="submissions",
    )

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
