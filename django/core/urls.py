from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.views.generic.base import RedirectView
from django.urls import path, include
from django.http import HttpResponse

from rest_framework import routers

from rest_framework_swagger.views import get_swagger_view

from repository.urls import urlpatterns as repository_urls
from repository.views import PackageListView
from repository.api.v1.viewsets import PackageViewSet

from targets.urls import urlpatterns as target_urls
from targets.views import TargetListView
from targets.api.v1.viewsets import TargetViewSet

from social.urls import settings_urls


api_v1_router = routers.DefaultRouter()
api_v1_router.register(r'package', PackageViewSet, basename="package")

handler404 = "frontend.views.handle404"
handler500 = "frontend.views.handle500"

urlpatterns = [
    path('', TargetListView.as_view(), name="index"),
    path('auth/', include('social_django.urls', namespace='social')),
    path('logout/', LogoutView.as_view(), kwargs={'next_page': '/'}, name="logout"),
    path('apps/', include(target_urls)),
    path('mods/', include(repository_urls)),
    path('settings/', include(settings_urls)),
    path('favicon.ico', RedirectView.as_view(url="%s%s" % (settings.STATIC_URL, 'favicon.ico'))),
    path('djangoadmin/', admin.site.urls),
    path('healthcheck/', lambda request: HttpResponse("OK"), name="healthcheck"),
    path('api/v1/', include((api_v1_router.urls, "api-v1"), namespace="api-v1")),
]

swagger_view = get_swagger_view(title="Thunderstore API")
urlpatterns += [path("api/docs/", lambda r: swagger_view(r), name="swagger")]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
