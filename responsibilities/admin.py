from django.contrib import admin

from .models import Responsibility, Tag


class TagInline(admin.TabularInline):
    model = Responsibility.tags.through
    extra = 0


@admin.register(Responsibility)
class ResponsibilityAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "primary_employee", "secondary_employee")
    list_filter = ("organization",)
    inlines = (TagInline,)
    exclude = ("tags",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    list_filter = ("organization",)
    inlines = (TagInline,)
