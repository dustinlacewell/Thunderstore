from django.contrib import admin


from targets.models import Target
from targets.models import TargetVersion


class TargetVersionInline(admin.TabularInline):
    model = TargetVersion
    readonly_fields = (
        "date_added",
    )
    fields = (
        "version_number",
        "date_added",
        "is_active"
    )

    extra = 0


@admin.register(Target)
class TargetAdmin(admin.ModelAdmin):
    inlines = [
        TargetVersionInline,
    ]

    readonly_fields = (
        "slug",
        "date_added",
    )
    list_display = (
        "name",
        "slug",
        "version_number",
        "version_count",
        "is_active",
        "is_pinned",
    )
    list_filter = (
        "is_active",
        "is_pinned",
    )
    search_fields = (
        "name", "slug"
    )
