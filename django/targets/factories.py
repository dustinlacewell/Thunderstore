import factory

from core.factories import UserFactory

from .models import Target
from .models import TargetVersion


class TargetFactory(factory.DjangoModelFactory):
    class Meta:
        model = Target

    owner = factory.SubFactory(UploaderIdentityFactory)
    name = factory.Faker("first_name")


class TargetVersionFactory(factory.DjangoModelFactory):
    class Meta:
        model = TargetVersion

    package = factory.SubFactory(TargetFactory)
    icon = factory.django.ImageField(width=256, height=256)
    name = factory.Faker("first_name")
    version_number = "1.0.0"
