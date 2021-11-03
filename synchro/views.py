import typing
from datetime import datetime

from django.db.models import Q
from django.utils.dateparse import parse_datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response

from synchro.models import StockReading
from synchro.serializers import StockReadingSerializer


@api_view(["POST"])
def sync(request):
    last_sync_date: datetime = parse_datetime(request.data["last_sync_date"])
    newly_created_records: typing.List = request.data.get("newly_created_records", [])

    gtin_stock_reading_map: typing.Dict[str, StockReading] = {
        item.gtin: item
        for item in StockReading.objects.filter(
            Q(updated_at__gt=last_sync_date) | Q(gtin__in=[record["gtin"] for record in newly_created_records])
        )
    }

    for record in newly_created_records:
        record["generated_at"] = parse_datetime(record["generated_at"])
        record["expiration_date"] = parse_datetime(record["expiration_date"])

        if record["gtin"] not in gtin_stock_reading_map:  # newly created gtin
            StockReading.objects.create(
                gtin=record["gtin"],
                expiration_date=record["expiration_date"],
                updated_at=record["generated_at"],
            )
            continue

        stock_reading: StockReading = gtin_stock_reading_map[record["gtin"]]
        if stock_reading.updated_at < record["generated_at"]:
            stock_reading.expiration_date = record["expiration_date"]
            stock_reading.updated_at = record["generated_at"]
            stock_reading.save()
            del gtin_stock_reading_map[stock_reading.gtin]

    result: typing.List[StockReading] = [sr for _, sr in gtin_stock_reading_map.items()]

    return Response({"data": StockReadingSerializer(result, many=True).data})


@api_view(["GET"])
def stock_reading_records(request):
    records = StockReading.objects.all()
    return Response({"data": StockReadingSerializer(records, many=True).data})
