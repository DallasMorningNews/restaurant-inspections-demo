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
    list_display = [
        'establishment_name',
        'city',
        'zip_code',
        'latest_inspection_date',
        'latest_inspection_letter_grade',
        'latest_inspection_numeric_grade',
    ]
    list_filter = [
        'city',
        'zip_code',
        # 'latest_inspection_letter_grade',
        # 'latest_inspection_numeric_grade',
    ]
    search_fields = ['establishment_name', 'source_id', 'address']
