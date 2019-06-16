import uuid

from distutils.version import StrictVersion

from django.conf import settings
from django.db import models
from django.db.models import Case, When, Sum, Q, signals
from django.utils.functional import cached_property
from django.urls import reverse
from core.cache import CacheBustCondition, invalidate_cache


class PackageQueryset(models.QuerySet):
    def active(self):
        return (
            self
            .exclude(is_active=False)
            .exclude(~Q(versions__is_active=True))
        )


class Package(models.Model):
    objects = PackageQueryset.as_manager()
    owner = models.ForeignKey(
        "repository.UploaderIdentity",
        on_delete=models.PROTECT,
        related_name="owned_packages",
    )
    name = models.CharField(
        max_length=128,
    )
    is_active = models.BooleanField(
        default=True,
    )
    is_deprecated = models.BooleanField(
        default=False,
    )
    date_created = models.DateTimeField(
        auto_now_add=True,
    )
    date_updated = models.DateTimeField(
        auto_now_add=True,
    )
    uuid4 = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )
    is_pinned = models.BooleanField(
        default=False,
    )
    latest = models.ForeignKey(
        "repository.PackageVersion",
        on_delete=models.SET_NULL,
        related_name="+",
        null=True,
    )

    class Meta:
        unique_together = ("owner", "name")

    @property
    def full_package_name(self):
        return f"{self.owner.name}-{self.name}"

    @property
    def display_name(self):
        return self.name.replace("_", " ")

    @cached_property
    def available_versions(self):
        # TODO: Caching
        versions = self.versions.filter(is_active=True).values_list("pk", "version_number")
        ordered = sorted(versions, key=lambda version: StrictVersion(version[1]))
        pk_list = [version[0] for version in reversed(ordered)]
        preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(pk_list)])
        return self.versions.filter(pk__in=pk_list).order_by(preserved)

    @property
    def version_count(self):
        return self.available_versions.count()

    @property
    def latest(self):
        return self.available_versions.last()

    def version_number(self):
        return self.latest.version_number
    version_number.short_description = 'Latest Version'

    @cached_property
    def downloads(self):
        # TODO: Caching
        return self.versions.aggregate(downloads=Sum("downloads"))["downloads"]

    @property
    def icon(self):
        return self.latest.icon

    @property
    def website_url(self):
        return self.latest.website_url

    @property
    def version_number(self):
        return self.latest.version_number

    @property
    def description(self):
        return self.latest.description

    @property
    def dependencies(self):
        return self.latest.dependencies.all()

    @cached_property
    def sorted_dependencies(self):
        return (
            self.latest.dependencies
            .select_related("package")
            .annotate(total_downloads=Sum("package__versions__downloads"))
            .order_by("-package__is_pinned", "-total_downloads")
        )

    @cached_property
    def is_effectively_active(self):
        return (
            self.is_active and
            self.versions.filter(is_active=True).count() > 0
        )

    @cached_property
    def dependants(self):
        # TODO: Caching
        return Package.objects.exclude(~Q(
            versions__dependencies__package=self,
        )).active()

    @property
    def owner_url(self):
        return reverse("packages.list_by_owner", kwargs={"owner": self.owner.name})

    @property
    def dependants_url(self):
        return reverse(
            "packages.list_by_dependency",
            kwargs={
                "owner": self.owner.name,
                "name": self.name,
            }
        )

    @property
    def readme(self):
        return self.latest.readme

    def get_absolute_url(self):
        return reverse(
            "packages.detail",
            kwargs={"owner": self.owner.name, "name": self.name}
        )

    @property
    def full_url(self):
        return "%(protocol)s%(hostname)s%(path)s" % {
            "protocol": settings.PROTOCOL,
            "hostname": settings.SERVER_NAME,
            "path": self.get_absolute_url()
        }

    def __str__(self):
        return self.full_package_name

    @staticmethod
    def post_save(sender, instance, **kwargs):
        invalidate_cache(CacheBustCondition.any_package_updated)

    @staticmethod
    def post_delete(sender, instance, **kwargs):
        invalidate_cache(CacheBustCondition.any_package_updated)


signals.post_save.connect(Package.post_save, sender=Package)
signals.post_delete.connect(Package.post_delete, sender=Package)
