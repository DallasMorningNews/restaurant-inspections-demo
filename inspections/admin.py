# Imports from Django.  # NOQA
from django.contrib import admin


# Imports from inspections.
from inspections.models import Establishment, Inspection, Violation  # NOQA


# Imports from other dependencies.
import nested_admin


class ViolationInline(nested_admin.NestedStackedInline):
    model = Violation
    classes = ('collapse',)


class InspectionInline(nested_admin.NestedTabularInline):
    model = Inspection
    classes = ('collapse',)
    inlines = [ViolationInline]


@admin.register(Establishment)
class EstablishmentAdmin(nested_admin.NestedModelAdmin):
    inlines = [
        InspectionInline,
    ]
