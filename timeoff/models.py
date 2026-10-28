import datetime

from django.db import models
from django.db.models import Q
from django.utils.translation import gettext as _

from people.models import Employee
from responsibilities.models import Responsibility


class TimeOffRequest(models.Model):
    class Meta:
        verbose_name = _("Time Off Request")
        verbose_name_plural = _("Time Off Requests")
        ordering = ordering = ["id"]

    employee = models.ForeignKey("people.Employee", on_delete=models.CASCADE)
    start_date = models.DateField(auto_now=False, auto_now_add=False)
    end_date = models.DateField(auto_now=False, auto_now_add=False)
    start_time = models.TimeField(
        auto_now=False, auto_now_add=False, blank=True, null=True
    )
    end_time = models.TimeField(
        auto_now=False, auto_now_add=False, blank=True, null=True
    )
    note = models.TextField(blank=True, null=True,
        help_text="Visible to team members")
    private_note = models.TextField(blank=True, null=True,
        help_text="Visible only to manager")
    acknowledged = models.BooleanField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    acknowledged_at = models.DateTimeField(blank=True, null=True)

    # TODO: Duplicated in TimeOffRequestViewSet action conflicting_responsibilities. Use a generic helper function to handle both?
    # TODO: Cached property? When/how to break cache?
    @property
    # A list of employees with time off requests in the same time period with
    # shared/backup responsibilities.
    def conflicting_responsibilities(self):
        start_year, start_month, start_day = self.start_date.year, self.start_date.month, self.start_date.day
        end_year, end_month, end_day = self.end_date.year, self.end_date.month, self.end_date.day
        employee = self.employee

        # Get all the employees that share a responsibility with this employee
        responsibility_buddies = Employee.objects.filter(
            Q(primary_responsibilities__in=employee.secondary_responsibilities.all()) |
            Q(secondary_responsibilities__in=employee.primary_responsibilities.all())
        ).distinct()

        # Get all the time off requests for those employees that conflict with
        # this request.
        conflicting_tors = TimeOffRequest.objects\
            .filter(employee__in=responsibility_buddies)\
            .exclude(employee=employee)\
            .exclude(start_date__gt=datetime.date(int(end_year), int(end_month), int(end_day)))\
            .exclude(end_date__lt=datetime.date(int(start_year), int(start_month), int(start_day)))

        # Prune the buddy list of any employees that don't have any conflicting
        # time off requests, and then annotate them with the list of shared
        # responsibilities.
        # First pass: Remove any responsibility buddies that don't have
        # conflicting time off requests.
        for buddy in responsibility_buddies:
            remove_buddy = True
            for tor in conflicting_tors:
                if tor.employee == buddy:
                    remove_buddy = False
            if remove_buddy:
                responsibility_buddies = responsibility_buddies.exclude(pk=buddy.pk)
        # Second pass: Add the responsibility names to the serialized
        # employees.
        for buddy in responsibility_buddies:
            for tor in conflicting_tors:
                if tor.employee == buddy:
                    conflicting_responsibilities = Responsibility.objects.filter(
                        (Q(primary_employee=employee) & Q(secondary_employee=buddy)) |
                        (Q(secondary_employee=employee) & Q(primary_employee=buddy))
                    )
                    buddy.responsibility_names = [r.name for r in conflicting_responsibilities]
        
        return responsibility_buddies


class TimeOffRequestTemporaryApprover(models.Model):
    """
    Manually set approvers in-stead of an employee for a given time period.
    During this period, approvals that would have gone to this person would
    also go to someone else.
    """
    employee_on_leave = models.ForeignKey("people.Employee",
        related_name="time_off_request_approvers_on_leave",
        on_delete=models.CASCADE)
    employee_in_stead = models.ForeignKey("people.Employee",
        related_name="time_off_request_approvers_in_stead",
        on_delete=models.CASCADE)
    start_date = models.DateField(auto_now=False, auto_now_add=False)
    end_date = models.DateField(auto_now=False, auto_now_add=False)