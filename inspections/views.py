# Imports from Django.  # NOQA
from django.views.generic.detail import DetailView
from django.views.generic import TemplateView


# Imports from inspections.
from inspections.models import Establishment
# from inspections.models import Establishment, Inspection, Violation  # NOQA


class InspectionsHomepageView(TemplateView):
    template_name = 'inspections/hello_world.html'


class RestaurantDetailView(DetailView):
    model = Establishment

    template_name = 'inspections/detail_view.html'


class RestaurantCardView(DetailView):
    model = Establishment

    template_name = 'inspections/card_view.html'
