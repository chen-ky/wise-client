import pytest
from wise_client.base_client import BaseClient, SANDBOX_BASE_URL, BASE_URL
from wise_client import HTTPStatusError
from pytest_httpx import HTTPXMock

# Match <base_url> or <base_url>/ or <base_url>/<endpoints>
# MOCK_URL = f"{SANDBOX_BASE_URL}/?.*"
APIKEY = "random_test"


class TestBaseClient():

    @pytest.mark.asyncio
    async def test_get_query(self, httpx_mock: HTTPXMock) -> None:
        expected_resp = {"message": "Success"}
        httpx_mock.add_response(json=expected_resp)
        client = BaseClient(api_key=APIKEY)
        actual_resp = await client.query()
        assert actual_resp == expected_resp  # nosec B101
        await client.disconnect()

    @pytest.mark.asyncio
    async def test_post_query(self, httpx_mock: HTTPXMock) -> None:
        expected_resp = {"message": "Success"}
        dummy_post_data = {"stuff": None}
        httpx_mock.add_response(method="POST", json=expected_resp)
        client = BaseClient(api_key=APIKEY)
        actual_resp = await client.query(method="POST", data=dummy_post_data)
        assert actual_resp == expected_resp  # nosec B101
        await client.disconnect()

    @pytest.mark.asyncio
    async def test_unknown_method(self, httpx_mock: HTTPXMock) -> None:
        client = BaseClient(api_key=APIKEY)
        with pytest.raises(NotImplementedError):
            await client.query(method="ERR")
        await client.disconnect()

    @pytest.mark.asyncio
    async def test_1xx_response(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(status_code=100)
        client = BaseClient(api_key=APIKEY)
        with pytest.raises(HTTPStatusError):
            await client.query()
        await client.disconnect()

    @pytest.mark.asyncio
    async def test_201_response(self, httpx_mock: HTTPXMock) -> None:
        expected_resp = {"message": "Success"}
        httpx_mock.add_response(method="POST", status_code=201,
                                json=expected_resp)
        client = BaseClient(api_key=APIKEY)
        actual_resp = await client.query(method="POST")
        assert actual_resp == expected_resp  # nosec B101
        await client.disconnect()

    @pytest.mark.asyncio
    async def test_4xx_response(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(status_code=401)
        client = BaseClient(api_key=APIKEY)
        with pytest.raises(HTTPStatusError):
            await client.query()
        await client.disconnect()

    @pytest.mark.asyncio
    async def test_5xx_response(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(status_code=500)
        client = BaseClient(api_key=APIKEY)
        with pytest.raises(HTTPStatusError):
            await client.query()
        await client.disconnect()

    def test_construct_url_sandbox(self):
        client = BaseClient(api_key=APIKEY)
        endpoint = "/v1/endpoint"
        expected_url = f"{SANDBOX_BASE_URL}{endpoint}"
        actual_url = client._construct_url(endpoint=endpoint)
        assert actual_url == expected_url  # nosec B101

    def test_construct_url_production(self):
        client = BaseClient(api_key=APIKEY, is_sandbox=False)
        endpoint = "/v1/endpoint"
        expected_url = f"{BASE_URL}{endpoint}"
        actual_url = client._construct_url(endpoint=endpoint)
        assert actual_url == expected_url  # nosec B101

    def test_construct_url_trailing_slash(self):
        client = BaseClient(api_key=APIKEY)
        endpoint = "/v1/endpoint//"
        expected_url = f"{SANDBOX_BASE_URL}{endpoint[:-2]}"  # Strip trailing /
        actual_url = client._construct_url(endpoint=endpoint)
        assert actual_url == expected_url  # nosec B101
