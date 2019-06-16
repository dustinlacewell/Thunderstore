from django.db import models, transaction
from django.utils.text import slugify

from repository.models import (UploaderIdentityMember,
                               UploaderIdentityMemberRole)


class UploaderIdentity(models.Model):
    name = models.CharField(
        max_length=64,
        unique=True,
    )

    slug = models.SlugField(
        max_length=128,
        unique=True,
        blank=True
    )

    class Meta:
        verbose_name = "Uploader Identity"
        verbose_name_plural = "Uploader Identities"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(UploaderIdentity, self).save(*args, **kwargs)

    @classmethod
    @transaction.atomic
    def get_or_create_for_user(cls, user):
        identity_membership = user.uploader_identities.first()
        if identity_membership:
            return identity_membership.identity

        identity, created = cls.objects.get_or_create(
            name=user.username,
        )
        if created:
            UploaderIdentityMember.objects.create(
                user=user,
                identity=identity,
                role=UploaderIdentityMemberRole.owner,
            )
        assert identity.members.filter(user=user).exists()
        return identity
