import typing
from datetime import datetime

from dateutil import parser
from django.db.models import Q
from django.utils.timezone import make_aware
from rest_framework.decorators import api_view
from rest_framework.response import Response

from synchro.models import StockReading
from synchro.serializers import StockReadingSerializer


def _parse_datetime(value: str) -> datetime:
    datetime_obj = parser.parse(value)
    if not datetime_obj.tzinfo:
        datetime_obj = make_aware(datetime_obj)
    print(datetime_obj)
    return datetime_obj


@api_view(["POST"])
def sync(request):
    last_sync_date: datetime = _parse_datetime(request.data["last_sync_date"])
    newly_created_records: typing.List = request.data.get("newly_created_records", [])

    gtin_stock_reading_map: typing.Dict[str, StockReading] = {
        item.gtin: item
        for item in StockReading.objects.filter(
            Q(updated_at__gt=last_sync_date) | Q(gtin__in=[record["gtin"] for record in newly_created_records])
        ).order_by("-updated_at")
    }

    for record in newly_created_records:
        record["updated_at"] = _parse_datetime(record["updated_at"])
        record["expiration_date"] = _parse_datetime(record["expiration_date"])

        # if the GTIN is not in the database we created a new record, this will not be returned to the user,
        # as he already has the record
        if record["gtin"] not in gtin_stock_reading_map:  # newly created gtin
            StockReading.objects.create(
                gtin=record["gtin"],
                expiration_date=record["expiration_date"],
                updated_at=record["updated_at"],
            )
            continue

        stock_reading: StockReading = gtin_stock_reading_map[record["gtin"]]
        # if the datebase reading is older than the sent record we updated the database
        # and we deleted the object from the readings that will be returned to the user as it has the updated reading
        if stock_reading.updated_at < record["updated_at"]:
            stock_reading.expiration_date = record["expiration_date"]
            stock_reading.updated_at = record["updated_at"]
            stock_reading.save()
            del gtin_stock_reading_map[stock_reading.gtin]

        # if the datebase reading is equal we don't include this reading to the returned results
        # as the user already has this reading
        elif stock_reading.updated_at == record["updated_at"]:
            del gtin_stock_reading_map[stock_reading.gtin]

        # if the database reading is more updated ,
        # we keep the record to the data that will be sent to the user so he can update his record

    result: typing.List[StockReading] = [sr for _, sr in gtin_stock_reading_map.items()]

    return Response({"data": StockReadingSerializer(result, many=True).data})


@api_view(["GET"])
def stock_readings(request):
    readings = StockReading.objects.all().order_by("-updated_at")
    return Response({"data": StockReadingSerializer(readings, many=True).data})
