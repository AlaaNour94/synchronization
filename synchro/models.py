from django.db import models

# Create your models here.

class StockReading(models.Model):
    gtin = models.CharField(max_length=250, unique=True)
    updated_at = models.DateTimeField()