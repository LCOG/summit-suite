from django.contrib import admin

from submissions.models import MileageSubmission, MileageSubmissionRow, Role, Submission


class MileageSubmissionRowInline(admin.TabularInline):
    model = MileageSubmissionRow
    extra = 0


@admin.register(MileageSubmission)
class MileageSubmissionAdmin(admin.ModelAdmin):
    list_display = (
        "id", "submission__submitter", "submission__organization",
        "submission__created_at", "submission__updated_at"
    )
    list_filter = ("submission__organization",)
    search_fields = (
        "submission__submitter__user__username",
        "submission__submitter__user__email"
    )
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
        "created_at",
    )
    list_filter = ("form_type", "status", "organization")
    search_fields = ("submitter__user__username", "submitter__user__email")


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "organization", "members_list")
    list_filter = ("organization",)
    search_fields = ("name",)
    filter_horizontal = ("members",)

    # Avoid many queries when getting members to display in list
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('members')

    def members_list(self, obj):
        return ",\n".join([employee.name for employee in obj.members.all()])
