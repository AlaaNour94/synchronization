from rest_framework import serializers

from synchro.models import StockReading


class StockReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockReading
        fields = ["gtin", "updated_at", "expiration_date"]
