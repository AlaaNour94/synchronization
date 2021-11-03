import pytest

from synchro.tests.factories import *  # noqa


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient

    return APIClient()
