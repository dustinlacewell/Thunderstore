from rest_framework.serializers import SerializerMethodField, ModelSerializer

from targets.models import Target, TargetVersion


class TargetVersionSerializer(ModelSerializer):
    full_name = SerializerMethodField()

    def get_full_name(self, instance):
        return instance.full_version_name

    class Meta:
        model = TargetVersion
        fields = (
            "full_name",
            "icon",
            "version_number",
            "date_created",
            "is_active",
            "uuid4",
        )


class TargetSerializer(ModelSerializer):
    versions = SerializerMethodField()
    full_name = SerializerMethodField()

    def get_versions(self, instance):
        versions = instance.available_versions
        return TargetVersionSerializer(versions, many=True, context=self._context).data

    def get_full_name(self, instance):
        return instance.full_target_name

    def get_target_url(self, instance):
        return instance.full_url

    class Meta:
        model = Target
        fields = (
            "name",
            "target_url",
            "date_created",
            "date_updated",
            "uuid4",
            "is_pinned",
            "is_deprecated",
            "versions",
        )
        depth = 0
