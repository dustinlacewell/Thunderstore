from django.contrib import admin


from targets.models import Target
from targets.models import TargetVersion


class TargetVersionInline(admin.StackedInline):
    model = TargetVersion
    readonly_fields = (
        "date_added",
    )
    extra = 0


@admin.register(Target)
class TargetAdmin(admin.ModelAdmin):
    inlines = [
        TargetVersionInline,
    ]

    readonly_fields = (
        "date_added",
    )
    list_display = (
        "name",
        "latest",
        "is_active",
        "is_pinned",
    )
    list_filter = (
        "is_active",
        "is_pinned",
    )
    search_fields = (
        "name",
    )
