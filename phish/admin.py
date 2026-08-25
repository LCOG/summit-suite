from django.contrib import admin

from .models import (
    PhishConfiguration, PhishGroup, PhishReport, PhishReportTask,
    PhishRiskProfile, PhishTask, SyntheticPhish, SyntheticPhishTemplate,
    TrainingAssignment, TrainingTemplate
)

class PhishReportTaskInline(admin.TabularInline):
    model = PhishReportTask
    extra = 0
    readonly_fields = ('task', 'completed_at', 'completed_by')

    
@admin.register(PhishReport)
class PhishReportAdmin(admin.ModelAdmin):
    list_display = ('employee', 'created_at', 'status', 'processed')
    readonly_fields = ('employee', 'created_at', 'message')
    search_fields = (
        'employee__user__first_name', 'employee__user__last_name',
        'employee__user__email'
    )
    list_filter = ('employee__organization', 'created_at', 'status')
    inlines = [PhishReportTaskInline]


@admin.register(PhishTask)
class PhishTaskAdmin(admin.ModelAdmin):
    list_display = ('order', 'name', 'organization')
    search_fields = ('name',)
    list_filter = ('organization',)


@admin.register(SyntheticPhishTemplate)
class SyntheticPhishTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'version', 'subject', 'active')
    search_fields = ('name', 'subject')
    list_filter = ('active', 'organization',)


@admin.register(SyntheticPhish)
class SyntheticPhishAdmin(admin.ModelAdmin):
    list_display = ('employee', 'template', 'sent_at', 'clicked', 'reported')
    readonly_fields = (
        'employee', 'template', 'sent_at', 'click_token', 'clicked',
        'clicked_at', 'reported', 'reported_at'
    )
    search_fields = (
        'employee__user__first_name', 'employee__user__last_name',
        'employee__user__email', 'template__name'
    )
    list_filter = ('employee__organization', 'clicked', 'reported', 'sent_at')


@admin.register(TrainingTemplate)
class TrainingTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'version', 'active')
    search_fields = ('name',)
    list_filter = ('active', 'organization',)


@admin.register(TrainingAssignment)
class TrainingAssignmentAdmin(admin.ModelAdmin):
    list_display = ('employee', 'template', 'assigned_at', 'completed')
    readonly_fields = (
        'employee', 'template', 'assigned_at', 'completed', 'completed_at'
    )
    search_fields = (
        'employee__user__first_name', 'employee__user__last_name',
        'employee__user__email', 'template__name'
    )
    list_filter = ('employee__organization', 'template', 'completed', 'assigned_at')


class PhishConfigurationInline(admin.StackedInline):
    model = PhishConfiguration
    extra = 0
    max_num = 1
    can_delete = False


class PhishGroupInline(admin.StackedInline):
    model = PhishGroup
    extra = 0
    filter_horizontal = ('members',)


class PhishRiskProfileInline(admin.StackedInline):
    model = PhishRiskProfile
    extra = 0
    filter_horizontal = ('members',)