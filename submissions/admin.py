from django.contrib import admin

from submissions.models import MileageSubmission, MileageSubmissionRow, Role, Submission


class MileageSubmissionRowInline(admin.TabularInline):
    model = MileageSubmissionRow
    extra = 0


@admin.register(MileageSubmission)
class MileageSubmissionAdmin(admin.ModelAdmin):
    list_display = ("id", "submitter", "organization", "created_at", "updated_at")
    list_filter = ("organization",)
    search_fields = ("submitter__user__username", "submitter__user__email")
    inlines = [MileageSubmissionRowInline]


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "form_type",
        "status",
        "submitter",
        "approver_role",
        "approved_by",
        "submitted_at",
    )
    list_filter = ("form_type", "status", "organization")
    search_fields = ("submitter__user__username", "submitter__user__email")


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "organization")
    list_filter = ("organization",)
    search_fields = ("name",)
