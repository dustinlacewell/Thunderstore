from django.contrib.postgres.search import TrigramSimilarity, SearchVector, SearchQuery
from django.db import transaction
from django.db.models import Q, Sum
from django.http import Http404
from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic import View

from targets.models import Target
from targets.models import TargetVersion

from django.shortcuts import redirect, get_object_or_404

# Should be divisible by 4 and 3
TARGETS_PER_PAGE = 24


class TargetListSearchView(ListView):
    model = Target
    paginate_by = TARGETS_PER_PAGE

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
            ("name", "Name"),
        )

    def get_active_ordering(self):
        ordering = self.request.GET.get("ordering", "name")
        possibilities = [x[0] for x in self.get_ordering_choices()]
        if ordering not in possibilities:
            return possibilities[0]
        return ordering

    def get_search_query(self):
        return self.request.GET.get("q", "")

    def order_queryset(self, queryset):
        active_ordering = self.get_active_ordering()
        if active_ordering == "name":
            return queryset.order_by("name")
        return queryset.order_by("name")

    def perform_search(self, queryset, search_query):
        search_fields = ("name", )

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
            "url": reverse_lazy("targets.list"),
            "name": "Targets",
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


class TargetListView(TargetListSearchView):

    def get_page_title(self):
        return f"Apps and Games"

    def get_cache_vary(self):
        return "all"


class TargetDetailView(DetailView):
    model = Target

    def get_object(self, *args, **kwargs):
        slug = self.kwargs["slug"]
        target = (
            self.model.objects.active()
            .filter(slug=slug)
            .first()
        )
        if not target:
            raise Http404("No matching target found")
        return target

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        package = context["object"]
        return context


class TargetVersionDetailView(DetailView):
    model = TargetVersion

    def get_object(self):
        slug = self.kwargs["slug"]
        version = self.kwargs["version"]
        target = get_object_or_404(Target, slug=slug)
        version = get_object_or_404(TargetVersion, target=target, version_number=version)
        return version
