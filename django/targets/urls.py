from django.urls import path

from targets.views import TargetListView
from targets.views import TargetDetailView
from targets.views import TargetVersionDetailView


urlpatterns = [
    path(
        '',
        TargetListView.as_view(),
        name="targets.list"
    ),
    path(
        '<str:slug>/',
        TargetDetailView.as_view(),
        name="targets.detail"
    ),
    path(
        '<str:slug>/<str:version>/',
        TargetVersionDetailView.as_view(),
        name="targets.version.detail",
    ),
]
