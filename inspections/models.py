# Imports from Django.  # NOQA
from django.db import models


# one for every establishment
class Restaurant(models.Model):
    establishment_name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    latest_inspection_date = models.DateField()
    latest_inspection_score = models.IntegerField()
    # change if we do letter grade here

    def __unicode__(self):
        return self.establishment_name


# each restaurant has as many inspection classes as they've had inspections
class Inspection(models.Model):
    restaurant = models.ForeignKey(Restaurant)
    inspection_date = models.DateField()
    inspection_score = models.CharField(max_length=100)
    # to account for letter & number scores
    inspection_type = models.CharField(max_length=100)
    # can remove if you don't think is applicable
    inspection_area = models.CharField(max_length=100)
    # for special dropdowns

    def __unicode__(self):
        return '{}, {}, {}'.format(
            self.restaurant,
            self.inspection_date,
            self.inspection_score
        )


# each inspection has as many classes of violations as they had violations
# (possibly, we can change this logic)
class Violations(models.Model):
    inspection = models.ForeignKey(Inspection)
    violation_name = models.CharField(max_length=250)
    violation_num = models.IntegerField()
    violation_details = models.TextField()

    def __unicode__(self):
        return '{}, {}, {}'.format(
            self.inspection,
            self.violation_name,
            self.violation_num
        )
