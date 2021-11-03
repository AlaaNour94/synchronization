from datetime import timedelta

from django.utils import timezone

from synchro.models import StockReading


class TestSunchronization:
    def test_client_can_retrieve_newly_updated_items(self, api_client, stock_reading_factory):

        stock_reading_factory.create_batch(5)

        last_sync_date = timezone.now() - timedelta(days=5)
        response = api_client.post("/v1/sync/", data={"last_sync_date": last_sync_date})
        assert len(response.json()["data"]) == 5

    def test_client_can_partialy_retrieve_newly_updated_items(self, api_client, stock_reading_factory):

        stock_reading_factory.create_batch(1)
        stock_reading_factory(updated_at=timezone.now() - timedelta(days=6))
        stock_reading_factory(updated_at=timezone.now() - timedelta(days=5))
        last_sync_date = timezone.now() - timedelta(days=5)
        response = api_client.post("/v1/sync/", data={"last_sync_date": last_sync_date})
        assert len(response.json()["data"]) == 1

    def test_client_can_write_new_data(self, api_client, stock_reading_factory):
        reading1 = stock_reading_factory(updated_at=timezone.now() - timedelta(days=6))
        stock_reading_factory(updated_at=timezone.now() - timedelta(days=7))
        last_sync_date = timezone.now() - timedelta(days=5)

        generated_at = timezone.now()

        response = api_client.post(
            "/v1/sync/",
            data={
                "last_sync_date": last_sync_date,
                "newly_created_records": [
                    {
                        "generated_at": generated_at,
                        "gtin": reading1.gtin,
                        "expiration_date": timezone.now() - timedelta(days=1),
                    }
                ],
            },
        )
        assert len(response.json()["data"]) == 0
        reading1.refresh_from_db()
        assert reading1.updated_at == generated_at

    def test_client_can_write_and_get_new_data(self, api_client, stock_reading_factory):

        stock_reading_factory.create_batch(1)
        reading1 = stock_reading_factory(updated_at=timezone.now() - timedelta(days=6))
        stock_reading_factory(updated_at=timezone.now() - timedelta(days=7))
        last_sync_date = timezone.now() - timedelta(days=5)

        generated_at = timezone.now()

        response = api_client.post(
            "/v1/sync/",
            data={
                "last_sync_date": last_sync_date,
                "newly_created_records": [
                    {
                        "generated_at": generated_at,
                        "gtin": reading1.gtin,
                        "expiration_date": timezone.now() - timedelta(days=1),
                    }
                ],
            },
        )
        assert len(response.json()["data"]) == 1
        reading1.refresh_from_db()
        assert reading1.updated_at == generated_at

    def test_client_can_create_new_gtin(self, api_client, stock_reading_factory):

        generated_at = timezone.now()

        reading1 = stock_reading_factory(updated_at=generated_at)

        response = api_client.post(
            "/v1/sync/",
            data={
                "last_sync_date": timezone.now() - timedelta(days=5),
                "newly_created_records": [
                    {
                        "generated_at": timezone.now() - timedelta(days=5),
                        "gtin": reading1.gtin,
                        "expiration_date": timezone.now() - timedelta(days=1),
                    },
                    {
                        "generated_at": generated_at,
                        "gtin": "new_gtin",
                        "expiration_date": timezone.now() - timedelta(days=1),
                    },
                ],
            },
        )
        assert len(response.json()["data"]) == 1
        reading1.refresh_from_db()
        assert reading1.updated_at == generated_at
        assert StockReading.objects.count() == 2
