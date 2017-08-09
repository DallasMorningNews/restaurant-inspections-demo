from django.db import models

# one for every establishment
class Restaurant(models.Model):
    establishment_name = models.CharField(max_length=100)
    source_id = models.IntegerField()
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    zip = models.IntegerField()

    def __unicode__(self):
        return self.establishment_name

# each restaurant has as many inspection classes as they've had inspections
class Inspection(models.Model):
    restaurant = models.ForeignKey(Restaurant)
    area = models.CharField(max_length=100)
    date = models.DateField()
    type = models.CharField(max_length=100)
    raw_score = models.CharField(max_length=100)

    def __unicode__(self):
        return self.restaurant + ", " + self.date + ", " + self.raw_score

# each inspection has as many classes of violations as they had violations (possibly, we can change this logic)
class Violations(models.Model):
    inspection = models.ForeignKey(Inspection)
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
