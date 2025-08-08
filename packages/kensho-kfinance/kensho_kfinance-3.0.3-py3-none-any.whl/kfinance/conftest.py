from datetime import datetime

import pytest
from requests_mock import Mocker

from kfinance.client.kfinance import Client


SPGI_COMPANY_ID = 21719
SPGI_SECURITY_ID = 2629107
SPGI_TRADING_ITEM_ID = 2629108


@pytest.fixture
def mock_client(requests_mock: Mocker) -> Client:
    """Create a KFinanceApiClient with a mock response for the SPGI id triple."""

    client = Client(refresh_token="foo")
    # Set access token so that the client doesn't try to fetch it.
    client.kfinance_api_client._access_token = "foo"  # noqa: SLF001
    client.kfinance_api_client._access_token_expiry = int(datetime(2100, 1, 1).timestamp())  # noqa: SLF001

    # Create a mock for the SPGI id triple.
    requests_mock.get(
        url="https://kfinance.kensho.com/api/v1/id/SPGI",
        json={
            "trading_item_id": SPGI_TRADING_ITEM_ID,
            "security_id": SPGI_SECURITY_ID,
            "company_id": SPGI_COMPANY_ID,
        },
    )
    requests_mock.get(
        url="https://kfinance.kensho.com/api/v1/id/MSFT",
        json={"trading_item_id": 2630413, "security_id": 2630412, "company_id": 21835},
    )

    # Create mock security id and trading item id for company ids 1 and 2:
    for company_id in [1, 2]:
        requests_mock.get(
            url=f"https://kfinance.kensho.com/api/v1/securities/{company_id}/primary",
            json={"primary_security": company_id},
        )
        requests_mock.get(
            url=f"https://kfinance.kensho.com/api/v1/trading_items/{company_id}/primary",
            json={"primary_trading_item": company_id},
        )

    return client
