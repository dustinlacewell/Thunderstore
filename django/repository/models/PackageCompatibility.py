from django.db import models

from repository.models import PackageVersion
from targets.models import Target, TargetVersion


class PackageCompatibility(models.Model):
    package_version = models.ForeignKey(PackageVersion, models.CASCADE)
    target = models.ForeignKey(Target, models.CASCADE)
    min_version = models.ForeignKey(
        TargetVersion,
        on_delete=models.SET_NULL,
        null=True,
        related_name='min_version')
    max_version = models.ForeignKey(
        TargetVersion,
        on_delete=models.SET_NULL,
        null=True,
        related_name='max_version')
