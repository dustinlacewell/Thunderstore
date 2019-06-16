from django.urls import path
from django.views.generic.base import RedirectView

from targets.views import TargetListView
from repository.views import PackageListView
from repository.views import PackageDetailView
from repository.views import PackageCreateView
from repository.views import PackageDownloadView
from repository.views import PackageListByOwnerView
from repository.views import PackageListByDependencyView
from repository.views import PackageVersionDetailView


urlpatterns = [
    path(
        '',
        RedirectView.as_view(pattern_name="targets.list"),
        name="packages.list"
    ),
    path(
        'upload/',
        PackageCreateView.as_view(),
        name="packages.create"
    ),
    path(
        '<str:owner>/<str:name>/<str:version>/download',
        PackageDownloadView.as_view(),
        name="packages.download"
    ),
    path(
        '<str:owner>/<str:name>/',
        PackageDetailView.as_view(),
        name="packages.detail"
    ),
    path(
        '<str:owner>/<str:name>/dependants/',
        PackageListByDependencyView.as_view(),
        name="packages.list_by_dependency"
    ),
    path(
        '<str:owner>/<str:name>/<str:version>/',
        PackageVersionDetailView.as_view(),
        name="packages.version.detail",
    ),
    path(
        '<str:owner>/',
        PackageListByOwnerView.as_view(),
        name="packages.list_by_owner",
    ),
]
