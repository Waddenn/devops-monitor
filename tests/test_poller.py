import pytest

from api.models import Server
from api.poller import poll_server


class FakeResponse:
    def __init__(self, status_code):
        self.status_code = status_code


class FakeAsyncClient:
    status_code = 200

    def __init__(self, timeout):
        self.timeout = timeout

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        return None

    async def get(self, url):
        return FakeResponse(self.status_code)


class FailingAsyncClient(FakeAsyncClient):
    async def get(self, url):
        raise OSError("connection failed")


def test_server_base_url_uses_https_for_port_443():
    server = Server(id=1, name="api", host="example.com", port=443)

    assert server.base_url() == "https://example.com:443"


@pytest.mark.anyio
async def test_poll_server_marks_up(monkeypatch):
    monkeypatch.setattr("api.poller.httpx.AsyncClient", FakeAsyncClient)
    server = Server(id=1, name="api", host="example.com", port=443)

    result = await poll_server(server)

    assert result.status == "UP"


@pytest.mark.anyio
async def test_poll_server_marks_degraded_on_non_200(monkeypatch):
    FakeAsyncClient.status_code = 503
    monkeypatch.setattr("api.poller.httpx.AsyncClient", FakeAsyncClient)
    server = Server(id=1, name="api", host="example.com", port=443)

    result = await poll_server(server)

    assert result.status == "DEGRADED"
    FakeAsyncClient.status_code = 200


@pytest.mark.anyio
async def test_poll_server_marks_down_on_error(monkeypatch):
    monkeypatch.setattr("api.poller.httpx.AsyncClient", FailingAsyncClient)
    server = Server(id=1, name="api", host="example.com", port=443)

    result = await poll_server(server)

    assert result.status == "DOWN"
