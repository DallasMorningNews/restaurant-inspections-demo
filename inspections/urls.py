# Imports from Django.  # NOQA
from django.conf.urls import url


# Imports from inspections.
from inspections.views import (  # NOQA
    InspectionsHomepageView,
    RestaurantCardView,
    RestaurantDetailView
)


urlpatterns = [
    url(
        r'^$',
        InspectionsHomepageView.as_view(),
        name='inspections-homepage'
    ),
    url(
        r'^restaurants/$',
        InspectionsHomepageView.as_view(),
        name='restaurant-list'
    ),
    url(
        r'^restaurants/(?P<pk>[0-9]+)/$',
        RestaurantDetailView.as_view(),
        name='restaurant-detail'
    ),
    url(
        r'^restaurants/(?P<pk>[0-9]+)/card/$',
        RestaurantCardView.as_view(),
        name='restaurant-card'
    ),
]
