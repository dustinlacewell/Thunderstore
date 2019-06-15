from rest_framework import viewsets

from core.cache import ManualCacheMixin, CacheBustCondition

from targets.api.v1.serializers import (
    TargetSerializer,
)
from targets.cache import get_target_list_queryset


class TargetViewSet(ManualCacheMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = TargetSerializer
    lookup_field = "uuid4"
    cache_until = CacheBustCondition.any_target_updated

    def get_queryset(self):
        return get_mod_list_queryset()
