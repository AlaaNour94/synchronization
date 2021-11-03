from django.db import models
from django.utils import timezone


class StockReading(models.Model):
    gtin = models.CharField(max_length=250, unique=True)
    updated_at = models.DateTimeField(default=timezone.now)
    expiration_date = models.DateTimeField()
