import uuid

from datetime import timedelta
from distutils.version import StrictVersion

from ipware import get_client_ip

from django.conf import settings
from django.core.files.storage import get_storage_class
from django.db import models, transaction
from django.db.models import Case, When, Sum, Q, signals
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property

from core.cache import CacheBustCondition, invalidate_cache
from core.utils import ChoiceEnum

from webhooks.models import Webhook, WebhookType


class TargetQueryset(models.QuerySet):
    def active(self):
        return (
            self
            .exclude(is_active=False)
            .exclude(~Q(versions__is_active=True))
        )

def get_version_png_filepath(instance, filename):
    return f"{instance.slug}.png"

class Target(models.Model):
    objects = TargetQueryset.as_manager()

    name = models.CharField(
        max_length=128,
    )
    slug = models.SlugField(
        max_length=128,
        unique=True,
    )
    uuid4 = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )
    is_active = models.BooleanField(
        default=True,
    )
    date_added = models.DateTimeField(
        auto_now_add=True,
    )
    date_updated = models.DateTimeField(
        auto_now_add=True,
    )
    is_pinned = models.BooleanField(
        default=False,
    )
    description = models.CharField(
        max_length=256
    )
    website_url = models.CharField(
        max_length=1024,
    )

    # <slug>.png
    icon = models.ImageField(
        upload_to=get_version_png_filepath,
    )

    @cached_property
    def available_versions(self):
        # TODO: Caching
        versions = self.versions.filter(is_active=True).values_list("pk", "version_number")
        ordered = sorted(versions, key=lambda version: version[1])
        pk_list = [version[0] for version in reversed(ordered)]
        preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(pk_list)])
        return self.versions.filter(pk__in=pk_list).order_by(preserved)

    @property
    def latest(self):
        return self.available_versions.last()

    @property
    def version_number(self):
        return self.latest.version_number

    @cached_property
    def is_effectively_active(self):
        return (
            self.is_active and
            self.versions.filter(is_active=True).count() > 0
        )

    def get_absolute_url(self):
        return reverse(
            "targets.detail",
            kwargs={"slug": self.slug}
        )

    @property
    def full_url(self):
        return "%(protocol)s%(hostname)s%(path)s" % {
            "protocol": settings.PROTOCOL,
            "hostname": settings.SERVER_NAME,
            "path": self.get_absolute_url()
        }

    def recache_latest(self):
        self.latest = self.available_versions.first()
        self.save()

    def handle_created_version(self, version):
        self.date_updated = timezone.now()

        if self.latest:
            new_version = version.version_number
            old_version = self.latest.version_number
            if new_version > old_version:
                self.latest = version
        else:
            self.latest = version
        self.save()

    def handle_deleted_version(self, version):
        self.recache_latest()

    def __str__(self):
        return self.name

    @staticmethod
    def post_save(sender, instance, created, **kwargs):
        invalidate_cache(CacheBustCondition.any_target_updated)

    @staticmethod
    def post_delete(sender, instance, created, **kwargs):
        invalidate_cache(CacheBustCondition.any_target_updated)


signals.post_save.connect(Target.post_save, sender=Target)
signals.post_delete.connect(Target.post_delete, sender=Target)


def get_version_png_filepath(instance, filename):
    return f"{instance}.png"


class TargetVersion(models.Model):
    target = models.ForeignKey(
        Target,
        related_name="versions",
        on_delete=models.CASCADE,
    )
    is_active = models.BooleanField(
        default=True,
    )
    date_added = models.DateTimeField(
        auto_now_add=True,
    )
    date_updated = models.DateTimeField(
        auto_now_add=True,
    )
    version_number = models.CharField(
        max_length=16,
    )
    uuid4 = models.UUIDField(
        default=uuid.uuid4,
        editable=False
    )

    class Meta:
        unique_together = ("target", "version_number")

    def get_absolute_url(self):
        return reverse(
            "targets.version.detail",
            kwargs={
                "slug": self.target.slug,
                "version": self.version_number
            }
        )

    @property
    def display_name(self):
        return self.target.name.replace("_", " ")

    @property
    def is_deprecated(self):
        return self.target.is_deprecated

    @property
    def full_version_name(self):
        return f"{self.target.name}-{self.version_number}"

    @staticmethod
    def post_save(sender, instance, created, **kwargs):
        if created:
            instance.target.handle_created_version(instance)

    @staticmethod
    def post_delete(sender, instance, **kwargs):
        instance.target.handle_deleted_version(instance)

    def __str__(self):
        return self.version_number


signals.post_save.connect(TargetVersion.post_save, sender=TargetVersion)
signals.post_delete.connect(TargetVersion.post_delete, sender=TargetVersion)
