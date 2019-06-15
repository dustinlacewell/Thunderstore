from repository.models import Package

from core.cache import (
    CacheBustCondition,
    cache_function_result
)


@cache_function_result(cache_until=CacheBustCondition.any_package_updated)
def get_target_list_queryset():
    return (
        Target.objects
        .active()
        .prefetch_related("versions")
        .order_by("-is_pinned", "is_deprecated", "-date_updated")
    )
