# Imports from python.  # NOQA
from datetime import datetime


# Imports from Django.
from django.db import models
from django.urls import reverse


VERBOSE_OVERRIDES = {
    'tarrant_county': 'Tarrant County',
}


INSPECTING_AGENCY_CHOICES = (
    ('carrollton', 'City of Carrollton'),
    ('dallas', 'City of Dallas'),
    ('fort_worth', 'City of Fort Worth'),
    ('plano', 'City of Plano'),
    ('richardson', 'City of Richardson'),
    ('tarrant_county', 'Tarrant County'),
)


class Establishment(models.Model):
    '''TK.

    There will be one Establishment instance for each establishment.
    '''
    establishment_name = models.CharField(max_length=200)
    source_id = models.CharField(max_length=50, blank=True, null=True)
    address = models.CharField(max_length=150)
    city = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return '{0} ({1}, TX)'.format(
            self.establishment_name,
            self.city
        )

    def get_absolute_url(self):
        return reverse('restaurant-detail', args=[str(self.id)])

    def latest_inspection_date(self):
        if self.inspection_set.count() > 0:
            return self.inspection_set.latest().date
        return None
    latest_inspection_date.short_description = "Latest inspection"

    latest_inspection_date = property(latest_inspection_date)

    def latest_inspection_letter_grade(self):
        if self.inspection_set.count() > 0:
            return self.inspection_set.latest().normalized_letter_grade
        return "?"
    latest_inspection_letter_grade.short_description = "Latest grade"

    latest_inspection_letter_grade = property(latest_inspection_letter_grade)

    def latest_inspection_numeric_grade(self):
        if self.inspection_set.count() > 0:
            return self.inspection_set.latest().normalized_numeric_grade
        return "--"
    latest_inspection_numeric_grade.short_description = "Latest score"

    latest_inspection_numeric_grade = property(latest_inspection_numeric_grade)


class Inspection(models.Model):
    '''TK.

    Each establishment has one inspection instance for each time it's
    been inspected.
    '''
    A_GRADE = 'A'
    B_GRADE = 'B'
    C_GRADE = 'C'
    D_GRADE = 'D'
    F_GRADE = 'F'

    LETTER_GRADE_CHOICES = (
        (A_GRADE, 'A'),
        (B_GRADE, 'B'),
        (C_GRADE, 'C'),
        (D_GRADE, 'D'),
        (F_GRADE, 'F'),
    )

    establishment = models.ForeignKey(Establishment)
    area = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateField()
    inspection_type = models.CharField(max_length=100, blank=True, null=True)
    raw_score = models.CharField(max_length=20)

    # The following fields get auto-generated by scrapers.
    source_agency = models.CharField(
        choices=INSPECTING_AGENCY_CHOICES,
        max_length=25
    )
    normalized_numeric_grade = models.IntegerField(blank=True, null=True)
    normalized_letter_grade = models.CharField(
        choices=LETTER_GRADE_CHOICES,
        max_length=1
    )

    class Meta:
        get_latest_by = "date"
        ordering = ['-date']

    def __str__(self):
        if self.area:
            return '{0} [{1}] on {2} ({3} grade)'.format(
                self.establishment,
                self.area,
                datetime.strftime(self.date, '%Y-%m-%d'),
                self.normalized_letter_grade
            )

        return '{0} on {1} ({2} grade)'.format(
            self.establishment,
            datetime.strftime(self.date, '%Y-%m-%d'),
            self.normalized_letter_grade
        )

    def displayed_violations(self):
        if self.violation_set.count() == 0:
            return []

        violations = []
        for _ in self.violation_set.all():
            if _.points_deducted == 0 and _.additional_information:
                pass
            else:
                violations.append(_)

        return violations
    displayed_violations = property(displayed_violations)

    def verbose_source_agency(self):
        if self.source_agency in VERBOSE_OVERRIDES:
            return VERBOSE_OVERRIDES['self.source_agency']

        return 'the {}'.format(
            # self.source_agency.replace('City', 'city')
            self.source_agency
        )
    verbose_source_agency = property(verbose_source_agency)

    def violations_count(self):
        if self.normalized_numeric_grade is None:
            return None
        return 100 - self.normalized_numeric_grade
    violations_count = property(violations_count)


class Violation(models.Model):
    '''TK.

    Each inspection has one violation instance for each violation that
    was recorded.
    '''
    inspection = models.ForeignKey(Inspection)
    points_deducted = models.IntegerField(blank=True, null=True)
    statute_citation = models.TextField(blank=True, null=True)
    infraction_category = models.TextField()
    inspector_comment = models.TextField()
    severity = models.CharField(max_length=25, blank=True, null=True)
    corrected_during_inspection = models.NullBooleanField()
    additional_information = models.TextField(blank=True, null=True)
    violation_count = models.IntegerField(blank=True, null=True)

    class Meta:
        ordering = ['-points_deducted', 'infraction_category']

    def __str__(self):
        return '"{0}" [{1} points deducted]'.format(
            self.infraction_category,
            self.points_deducted
        )
