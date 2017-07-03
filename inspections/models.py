from django.db import models

class Restaurant(models.Model):
    establishment_name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    latest_inspection_date = models.DateField()
    latest_inspection_score = models.IntegerField()

class PastInspection(models.Model):
    restaurant = models.ForeignKey(Restaurant)
