from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Count
from django.utils.translation import gettext_lazy as _

from mainsite.models import Organization
from people.models import Employee


class Role(models.Model):
    def __str__(self):
        return self.name

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    members = models.ManyToManyField(
        Employee, blank=True, related_name='purchase_roles'
    )


class PurchaseCategory(models.Model):
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'Purchase categories'

    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    role = models.ForeignKey(
        Role, blank=True, null=True, on_delete=models.SET_NULL
    )


class PurchaseObject(models.Model):
    def __str__(self):
        return self.name

    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(
        PurchaseCategory, blank=True, null=True, on_delete=models.SET_NULL
    )


class PurchaseRequest(models.Model):
    PR_STATUS_REQUESTED = 'requested'
    PR_STATUS_CANCELLED = 'cancelled'
    PR_STATUS_APPROVED = 'approved'
    PR_STATUS_REJECTED = 'rejected'
    PR_STATUS_ORDERED = 'ordered'
    PR_STATUS_RECEIVED = 'received'
    PR_STATUS_COMPLETE = 'complete'
    
    status_choices = (
        (PR_STATUS_REQUESTED, 'Requested'),
        (PR_STATUS_CANCELLED, 'Cancelled'),
        (PR_STATUS_APPROVED, 'Approved'),
        (PR_STATUS_REJECTED, 'Rejected'),
        (PR_STATUS_ORDERED, 'Ordered'),
        (PR_STATUS_RECEIVED, 'Received'),
        (PR_STATUS_COMPLETE, 'Complete')
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        Employee, blank=True, null=True, on_delete=models.SET_NULL,
        related_name='purchase_request_created_by',
    )
    updated_by = models.ForeignKey(
        Employee, blank=True, null=True, on_delete=models.SET_NULL,
        related_name='purchase_request_updated_by',
    )
    request_for = models.ForeignKey(
        Employee, blank=True, null=True, on_delete=models.SET_NULL,
        related_name='purchase_request_for',
    )
    purchase_object = models.ForeignKey(
        PurchaseObject, blank=True, null=True, on_delete=models.SET_NULL
    )
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)
    gl_code = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(
        max_length=255, blank=True, null=True, choices=status_choices
    )

    def save(self, *args, **kwargs):
        if not self.pk:
            self.status = self.PR_STATUS_REQUESTED
        super().save(*args, **kwargs)


class ExpenseBaseModel(models.Model):
    class Meta:
        abstract = True

    STATUS_DRAFT = 'draft'
    STATUS_SUBMITTED = 'submitted'
    STATUS_APPROVER_APPROVED = 'approver_approved'
    STATUS_APPROVER_DENIED = 'approver_denied'
    STATUS_DIRECTOR_APPROVED = 'director_approved'
    STATUS_DIRECTOR_DENIED = 'director_denied'
    STATUS_FISCAL_APPROVED = 'fiscal_approved'
    STATUS_FISCAL_DENIED = 'fiscal_denied'
    STATUS_CHOICES = (
        (STATUS_DRAFT, 'Draft'),
        (STATUS_SUBMITTED, 'Submitted'),
        (STATUS_APPROVER_APPROVED, 'Approver Approved'),
        (STATUS_APPROVER_DENIED, 'Approver Denied'),
        (STATUS_DIRECTOR_APPROVED, 'Director Approved'),
        (STATUS_DIRECTOR_DENIED, 'Director Denied'),
        (STATUS_FISCAL_APPROVED, 'Fiscal Approved'),
        (STATUS_FISCAL_DENIED, 'Fiscal Denied'),
    )

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE,
        related_name='%(class)ss'
    )
    status = models.CharField(
        max_length=17, choices=STATUS_CHOICES, default=STATUS_DRAFT
    )


class ExpenseGL(models.Model):
    class Meta:
        ordering = ["pk",]

    expense = models.ForeignKey(
        'Expense', on_delete=models.CASCADE, related_name='gls'
    )
    code = models.CharField(max_length=255, blank=True)
    job = models.CharField(max_length=255, blank=True)
    activity = models.CharField(max_length=7, blank=True)
    amount = models.DecimalField(
        _("dollar amount"), max_digits=10, decimal_places=2, blank=True,
        null=True
    )
    approver = models.ForeignKey(
        Employee, blank=True, null=True, on_delete=models.SET_NULL,
        related_name='expense_gls'
    )
    approved = models.BooleanField(default=False)
    approved_at = models.DateTimeField(blank=True, null=True)
    approver_note = models.TextField(blank=True)


class Expense(ExpenseBaseModel):
    class Meta:
        ordering = ["pk",]

    month = models.ForeignKey(
        'ExpenseMonth', on_delete=models.CASCADE, related_name='expenses'
    )
    name = models.CharField(max_length=255, blank=True)
    date = models.DateField(blank=True, null=True)
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    vendor = models.CharField(max_length=255, blank=True)
    receipt = models.FileField(
        _("receipt"), upload_to="uploads/expenses", blank=True, null=True
    )
    repeat = models.BooleanField(default=False)


class ExpenseMonth(ExpenseBaseModel):
    class Meta:
        ordering = ["pk",]
        unique_together = ['purchaser', 'month', 'year', 'card']

    def __str__(self):
        return f'{self.month}/{self.year} for {self.purchaser}'
    
    def save(self, *args, **kwargs):
        set_card = False
        if not self.pk:
            set_card = True
        super().save(*args, **kwargs)
        # If this is a new month, set the card to the submitter's default card
        if set_card:
            # Don't set the card if this would create a duplicate
            if ExpenseMonth.objects.filter(
                purchaser=self.purchaser, month=self.month, year=self.year
            ).count() > 1:
                return
            card = self.purchaser.expense_cards.first()
            if card:
                self.card = card
                self.save()

    year = models.IntegerField()
    month = models.IntegerField()
    purchaser = models.ForeignKey(
        Employee, blank=True, null=True, on_delete=models.SET_NULL,
        related_name='expense_months',
    )
    card = models.ForeignKey(
        'ExpenseCard', blank=True, null=True, on_delete=models.SET_NULL,
        related_name='expense_months'
    )

    # Submission info
    submitter_note = models.TextField(blank=True)
    submitted_at = models.DateTimeField(blank=True, null=True)
    
    # Approval info - Used only for Fiscal view to see who denied most recently
    # or when it was finally approved.
    denier_name = models.CharField(max_length=255, blank=True)
    approved_as_of = models.DateTimeField(blank=True, null=True)

    # Division Director approval info
    director_approved = models.BooleanField(default=False)
    director_approved_at = models.DateTimeField(blank=True, null=True)
    director_note = models.TextField(blank=True)

    # Fiscal approval info
    fiscal_approver = models.ForeignKey(
        Employee, blank=True, null=True, on_delete=models.SET_NULL,
        related_name='approver_of_expense_month',
    )
    fiscal_approved_at = models.DateTimeField(blank=True, null=True)
    fiscal_note = models.TextField(blank=True)


class ExpenseCard(models.Model):
    class Meta:
        ordering = ["pk",]
    
    def __str__(self):
        return f'*{self.last4}'

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE,
        related_name='expense_cards'
    )
    last4 = models.CharField(
        max_length=4,
        validators=[
            RegexValidator(
                regex='^[0-9]{4}$',
                message='Must be 4 digits'
            ),
        ]
    )
    assignee = models.ForeignKey(
        Employee, blank=True, null=True, on_delete=models.SET_NULL,
        related_name='expense_cards'
    )
    shared = models.BooleanField(default=False)
    requires_director_approval = models.BooleanField(default=False)
    director = models.ForeignKey(
        Employee, blank=True, null=True, on_delete=models.SET_NULL,
        related_name='approver_of_cards'
    )


class ExpenseStatement(models.Model):
    class Meta:
        ordering = ["pk",]

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE,
        related_name='expense_statements'
    )
    card = models.ForeignKey(
        ExpenseCard, on_delete=models.CASCADE, related_name='statements'
    )
    month = models.IntegerField()
    year = models.IntegerField()

    def all_cleared(self):
        """
        Return true if all items in the statement have been approved by fiscal
        in one or more ExpenseMonths.
        """
        if self.card.shared:
            # If the card is shared, the number of expenses in fiscal approved
            # expense months for the card need to match the number of items in
            # the statement.
            card_ems = ExpenseMonth.objects.filter(
                organization=self.organization, month=self.month,
                year=self.year, card=self.card,
                status=ExpenseMonth.STATUS_FISCAL_APPROVED,
            ).annotate(Count('expenses'))
            # Add up all ems expenses
            total_expenses = sum([em.expenses__count for em in card_ems])
            return total_expenses == self.items.count()
        else:
            # If the card is not shared, just verify that there is an approved
            # Expense Month
            return ExpenseMonth.objects.filter(
                organization=self.organization, month=self.month,
                year=self.year, card=self.card,
                status=ExpenseMonth.STATUS_FISCAL_APPROVED
            ).exists()


class ExpenseStatementItem(models.Model):
    class Meta:
        ordering = ["pk",]

    statement = models.ForeignKey(
        ExpenseStatement, on_delete=models.CASCADE, related_name='items'
    )
    date = models.DateField(_("Transaction Date"))
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)


class ExpenseMonthLock(models.Model):
    class Meta:
        ordering = ["pk",]

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE,
        related_name='expense_month_locks'
    )
    year = models.IntegerField()
    month = models.IntegerField()
    locked_at = models.DateTimeField(auto_now_add=True)
    locked_by = models.ForeignKey(
        Employee, blank=True, null=True, on_delete=models.SET_NULL,
        related_name='expense_month_locks'
    )