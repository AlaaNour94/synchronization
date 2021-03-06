import uuid

import factory
from django.utils import timezone
from pytest_factoryboy import register

from synchro.models import StockReading


@register
class StockReadingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = StockReading
        django_get_or_create = ("gtin",)

    gtin = factory.lazy_attribute(lambda _: str(uuid.uuid4()))
    expiration_date = timezone.now()
