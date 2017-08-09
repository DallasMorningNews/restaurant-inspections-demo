# Imports from Django.  # NOQA
from django.db import models


# one for every establishment
class Restaurant(models.Model):
    establishment_name = models.CharField(max_length=100)
    source_id = models.IntegerField()
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
<<<<<<< HEAD
    zip = models.IntegerField()
=======
    latest_inspection_date = models.DateField()
    latest_inspection_score = models.IntegerField()
    # change if we do letter grade here
>>>>>>> 751df9c5ec8f153fd5062d3cbeb3511f98074483

    def __unicode__(self):
        return self.establishment_name


# each restaurant has as many inspection classes as they've had inspections
class Inspection(models.Model):
    restaurant = models.ForeignKey(Restaurant)
<<<<<<< HEAD
    area = models.CharField(max_length=100)
    date = models.DateField()
    type = models.CharField(max_length=100)
    raw_score = models.CharField(max_length=100)

    def __unicode__(self):
        return self.restaurant + ", " + self.date + ", " + self.raw_score
=======
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

>>>>>>> 751df9c5ec8f153fd5062d3cbeb3511f98074483

# each inspection has as many classes of violations as they had violations
# (possibly, we can change this logic)
class Violations(models.Model):
    inspection = models.ForeignKey(Inspection)
<<<<<<< HEAD
    points_deducted = models.IntegerField()
    statute_citation = models.CharField(max_length=100)
    infraction_category = models.CharField(max_length=100)
    inspector_comment = models.CharField(max_length=100)
    severity = models.CharField(max_length=100)
    corrected_during_inspection = models.NullBooleanField()
    additional_information = models.CharField(max_length=100)
    violation_count = models.IntegerField()

    def __unicode__(self):
        return self.inspection + ", " + self.infraction_category + ", " + self.inspector_comment
=======
    violation_name = models.CharField(max_length=250)
    violation_num = models.IntegerField()
    violation_details = models.TextField()

    def __unicode__(self):
        return '{}, {}, {}'.format(
            self.inspection,
            self.violation_name,
            self.violation_num
        )
>>>>>>> 751df9c5ec8f153fd5062d3cbeb3511f98074483
