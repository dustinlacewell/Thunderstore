from django.contrib.postgres.search import TrigramSimilarity, SearchVector, SearchQuery
from django.db import transaction
from django.db.models import Q, Sum
from django.http import Http404
from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django.views.generic import View

from repository.models import Package
from repository.models import PackageVersion
from repository.models import UploaderIdentity
from repository.ziptools import PackageVersionForm

from django.shortcuts import redirect, get_object_or_404

# Should be divisible by 4 and 3
MODS_PER_PAGE = 24


class PackageListSearchView(ListView):
    model = Package
    paginate_by = MODS_PER_PAGE

    def get_base_queryset(self):
        return self.model.objects.active()

    def get_page_title(self):
        return ""

    def get_cache_vary(self):
        return ""

    def get_full_cache_vary(self):
        cache_vary = self.get_cache_vary()
        cache_vary += f".{self.get_search_query()}"
        cache_vary += f".{self.get_active_ordering()}"
        return cache_vary

    def get_ordering_choices(self):
        return (
            ("last-updated", "Last updated"),
            ("newest", "Newest"),
            ("most-downloaded", "Most downloaded")
        )

    def get_active_ordering(self):
        ordering = self.request.GET.get("ordering", "last-updated")
        possibilities = [x[0] for x in self.get_ordering_choices()]
        if ordering not in possibilities:
            return possibilities[0]
        return ordering

    def get_search_query(self):
        return self.request.GET.get("q", "")

    def order_queryset(self, queryset):
        active_ordering = self.get_active_ordering()
        if active_ordering == "newest":
            return queryset.order_by("-is_pinned", "is_deprecated", "-date_created")
        if active_ordering == "most-downloaded":
            return (
                queryset
                .annotate(total_downloads=Sum("versions__downloads"))
                .order_by("-is_pinned", "is_deprecated", "-total_downloads")
            )
        return queryset.order_by("-is_pinned", "is_deprecated", "-date_updated")

    def perform_search(self, queryset, search_query):
        search_fields = ("name", "slug", "owner__name", "owner__slug", "latest__description")

        icontains_query = Q()
        parts = search_query.split(" ")
        for part in parts:
            for field in search_fields:
                icontains_query &= ~Q(**{
                    f"{field}__icontains": part
                })

        return (
            queryset
            # .annotate(name_search_score=TrigramSimilarity("name", search_query))
            # .annotate(search=SearchVector(*search_fields))
            # .exclude(
            #     Q(name_search_score__lte=1) &
            #     ~Q(search=SearchQuery(search_query))
            # )
            .exclude(icontains_query)
            .distinct()
        )

    def get_queryset(self):
        queryset = (
            self.get_base_queryset()
            .prefetch_related("versions")
        )
        search_query = self.get_search_query()
        if search_query:
            queryset = self.perform_search(queryset, search_query)
        return self.order_queryset(queryset)

    def get_breadcrumbs(self):
        return [{
            "url": reverse_lazy("packages.list"),
            "name": "Packages",
        }]

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["cache_vary"] = self.get_full_cache_vary()
        context["page_title"] = self.get_page_title()
        context["ordering_modes"] = self.get_ordering_choices()
        context["active_ordering"] = self.get_active_ordering()
        context["current_search"] = self.get_search_query()
        breadcrumbs = self.get_breadcrumbs()
        if len(breadcrumbs) > 1:
            context["breadcrumbs"] = breadcrumbs
        return context


class PackageListView(PackageListSearchView):

    def get_page_title(self):
        return f"All mods"

    def get_cache_vary(self):
        return "all"


class PackageListByOwnerView(PackageListSearchView):

    def get_breadcrumbs(self):
        return []

    def cache_owner(self):
        self.owner = get_object_or_404(
            UploaderIdentity,
            name=self.kwargs["owner"]
        )

    def dispatch(self, *args, **kwargs):
        self.cache_owner()
        return super().dispatch(*args, **kwargs)

    def get_base_queryset(self):
        return self.model.objects.active().exclude(~Q(owner=self.owner))

    def get_page_title(self):
        return f"Mods uploaded by {self.owner.name}"

    def get_cache_vary(self):
        return f"authorer-{self.owner.slug}"


class PackageListByDependencyView(PackageListSearchView):
    model = Package
    paginate_by = MODS_PER_PAGE

    def cache_package(self):
        owner = self.kwargs["owner"]
        owner = get_object_or_404(UploaderIdentity, slug=owner)
        name = self.kwargs["name"]
        package = (
            self.model.objects.active()
            .filter(owner=owner, slug=name)
            .first()
        )
        if not package:
            raise Http404("No matching package found")
        self.package = package

    def dispatch(self, *args, **kwargs):
        self.cache_package()
        return super().dispatch(*args, **kwargs)

    def get_base_queryset(self):
        return self.package.dependants

    def get_page_title(self):
        return f"Mods that depend on {self.package.name}"

    def get_cache_vary(self):
        return f"dependencies-{self.package.id}"


class PackageDetailView(DetailView):
    model = Package

    def get_object(self, *args, **kwargs):
        owner = self.kwargs["owner"]
        owner = get_object_or_404(UploaderIdentity, slug=owner)
        name = self.kwargs["name"]
        package = (
            self.model.objects.active()
            .filter(owner=owner, slug=name)
            .first()
        )
        if not package:
            raise Http404("No matching package found")
        return package

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        dependants_string = ""
        package = context["object"]
        dependant_count = package.dependants.active().count()

        if dependant_count == 1:
            dependants_string = f"{dependant_count} other mod depends on this mod"
        else:
            dependants_string = f"{dependant_count} other mods depend on this mod"

        context["dependants_string"] = dependants_string
        return context


class PackageVersionDetailView(DetailView):
    model = PackageVersion

    def get_object(self):
        owner = self.kwargs["owner"]
        name = self.kwargs["name"]
        version = self.kwargs["version"]
        package = get_object_or_404(Package, owner__slug=owner, slug=name)
        version = get_object_or_404(PackageVersion, package=package, version_number=version)
        return version


class PackageCreateView(CreateView):
    model = PackageVersion
    form_class = PackageVersionForm
    template_name = "repository/package_create.html"

    def dispatch(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect("index")
        return super(PackageCreateView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(PackageCreateView, self).get_form_kwargs(*args, **kwargs)
        kwargs["owner"] = UploaderIdentity.get_or_create_for_user(
            self.request.user
        )
        return kwargs

    @transaction.atomic
    def form_valid(self, form):
        instance = form.save()
        return redirect(instance)


class PackageDownloadView(View):

    def get(self, *args, **kwargs):
        owner = kwargs["owner"]
        name = kwargs["name"]
        version = kwargs["version"]

        package = get_object_or_404(Package, owner__name=owner, name=name)
        version = get_object_or_404(PackageVersion, package=package, version_number=version)
        version.maybe_increase_download_counter(self.request)
        return redirect(self.request.build_absolute_uri(version.file.url))
