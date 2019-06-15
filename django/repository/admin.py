from django.contrib import admin


from repository.models import Package
from repository.models import PackageVersion
from repository.models import PackageCompatibility
from repository.models import UploaderIdentity
from repository.models import UploaderIdentityMember


class UploaderIdentityMemberAdmin(admin.StackedInline):
    model = UploaderIdentityMember
    extra = 0
    list_display = (
        "user",
        "identity",
        "role",
    )


@admin.register(UploaderIdentity)
class UploaderIdentityAdmin(admin.ModelAdmin):
    inlines = [
        UploaderIdentityMemberAdmin,
    ]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields
        else:
            return []

    readonly_fields = (
        "name",
    )
    list_display = (
        "name",
    )


class PackageVersionInline(admin.TabularInline):
    model = PackageVersion
    fields = (
        "version_number",
        "file",
        "downloads",
        "date_created",
        "is_active"
    )

    readonly_fields = (
        "date_created",
        "dependencies",
        "description",
        "downloads",
        "file",
        "icon",
        "name",
        "readme",
        "version_number",
        "website_url",
    )
    extra = 0
    filter_horizontal = ("dependencies",)

class PackageCompatibilityInline(admin.StackedInline):
    model = PackageCompatibility
    extra = 0

@admin.register(PackageVersion)
class PackageVersionAdmin(admin.ModelAdmin):
    inlines = [
        PackageCompatibilityInline
    ]

@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    inlines = [
        PackageVersionInline,
    ]

    readonly_fields = (
        "date_created",
        "downloads",
        "name",
        "owner",
        "version_number",
    )

    list_display = (
        "name",
        "owner",
        "version_number",
        "version_count",
        "downloads",
        "is_active",
        "is_deprecated",
        "is_pinned",
    )
    list_filter = (
        "is_active",
        "is_pinned",
        "is_deprecated",
    )
    search_fields = (
        "name",
        "owner__name",
    )
