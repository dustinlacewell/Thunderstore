import uuid

from ipware import get_client_ip

from django.conf import settings
from django.db import models
from django.core.files.storage import get_storage_class
from django.urls import reverse
from django.utils import timezone
from django.db.models import signals

from repository.models import Package
from webhooks.models import Webhook, WebhookType
from repository.utils import get_version_zip_filepath, get_version_png_filepath

class PackageVersion(models.Model):
    package = models.ForeignKey(
        "Package",
        related_name="versions",
        on_delete=models.CASCADE,
    )
    is_active = models.BooleanField(
        default=True,
    )
    date_created = models.DateTimeField(
        auto_now_add=True,
    )
    downloads = models.PositiveIntegerField(
        default=0
    )

    name = models.CharField(
        max_length=Package._meta.get_field("name").max_length,
    )
    version_number = models.CharField(
        max_length=16,
    )
    website_url = models.CharField(
        max_length=1024,
    )
    description = models.CharField(
        max_length=256
    )
    dependencies = models.ManyToManyField(
        "self",
        related_name="dependants",
        symmetrical=False,
        blank=True,
    )
    readme = models.TextField()

    # <packagename>.zip
    file = models.FileField(
        upload_to=get_version_zip_filepath,
        storage=get_storage_class(settings.PACKAGE_FILE_STORAGE)(),
    )
    # <packagename>.png
    icon = models.ImageField(
        upload_to=get_version_png_filepath,
    )
    uuid4 = models.UUIDField(
        default=uuid.uuid4,
        editable=False
    )

    class Meta:
        unique_together = ("package", "version_number")

    def get_absolute_url(self):
        return reverse(
            "packages.version.detail",
            kwargs={
                "owner": self.owner.name,
                "name": self.name,
                "version": self.version_number
            }
        )

    @property
    def display_name(self):
        return self.name.replace("_", " ")

    @property
    def owner_url(self):
        return self.package.owner_url

    @property
    def owner(self):
        return self.package.owner

    @property
    def is_deprecated(self):
        return self.package.is_deprecated

    @property
    def full_version_name(self):
        return f"{self.package.full_package_name}-{self.version_number}"

    @property
    def download_url(self):
        return reverse("packages.download", kwargs={
            "owner": self.package.owner.name,
            "name": self.package.name,
            "version": self.version_number,
        })

    @property
    def install_url(self):
        return "ror2mm://v1/install/%(hostname)s/%(owner)s/%(name)s/%(version)s/" % {
            "hostname": settings.SERVER_NAME,
            "owner": self.package.owner.name,
            "name": self.package.name,
            "version": self.version_number,
        }

    @staticmethod
    def post_save(sender, instance, created, **kwargs):
        if created:
            instance.announce_release()

    def announce_release(self):
        webhooks = Webhook.objects.filter(
            webhook_type=WebhookType.mod_release,
            is_active=True,
        )

        thumbnail_url = self.icon.url
        if not (thumbnail_url.startswith("http://") or thumbnail_url.startswith("https://")):
            thumbnail_url = f"{settings.PROTOCOL}{settings.SERVER_NAME}{thumbnail_url}"

        webhook_data = {
            "embeds": [{
                "title": f"{self.name} v{self.version_number}",
                "type": "rich",
                "description": self.description,
                "url": self.package.full_url,
                "timestamp": timezone.now().isoformat(),
                "color": 4474879,
                "thumbnail": {
                    "url": thumbnail_url,
                    "width": 256,
                    "height": 256,
                },
                "provider": {
                    "name": "Thunderstore",
                    "url": f"{settings.PROTOCOL}{settings.SERVER_NAME}/"
                },
                "author": {
                    "name": self.package.owner.name,
                },
                "fields": [{
                    "name": "Total downloads across versions",
                    "value": f"{self.package.downloads}",
                }]
            }]
        }

        for webhook in webhooks:
            webhook.call_with_json(webhook_data)

    def maybe_increase_download_counter(self, request):
        client_ip, is_routable = get_client_ip(request)
        if client_ip is None:
            return

        download_event, created = PackageVersionDownloadEvent.objects.get_or_create(
            version=self,
            source_ip=client_ip,
        )

        if created:
            valid = True
        else:
            valid = download_event.count_downloads_and_return_validity()

        if valid:
            self.downloads += 1
            self.save(update_fields=("downloads",))

    def __str__(self):
        return self.full_version_name


signals.post_save.connect(PackageVersion.post_save, sender=PackageVersion)

