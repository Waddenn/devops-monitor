import os

import pytest
from fastapi import HTTPException
from starlette.websockets import WebSocketDisconnect

from api import main
from api.auth import verify_api_key
from api.models import ServerIn


@pytest.fixture(autouse=True)
def reset_app_state(monkeypatch):
    monkeypatch.setenv("API_KEY", "test-secret")
    main._store.clear()
    main._counter = 0
    yield
    main._store.clear()
    main._counter = 0


@pytest.mark.anyio
async def test_health():
    response = await main.health_check()

    assert response == {"status": "ok"}


@pytest.mark.anyio
async def test_metrics():
    payload = await main.metrics()

    assert {"cpu_percent", "memory_percent", "disk_percent"} <= payload.keys()


def test_create_server_requires_api_key():
    with pytest.raises(HTTPException) as exc_info:
        verify_api_key(None)

    assert exc_info.value.status_code == 403


@pytest.mark.anyio
async def test_create_and_list_servers():
    verify_api_key(os.environ["API_KEY"])
    response = await main.register_server(
        ServerIn(name="api", host="httpbin.org", port=443, tags=["prod"])
    )

    assert response.status == "unknown"

    servers = await main.list_servers()
    assert len(servers) == 1
    assert servers[0].name == "api"


@pytest.mark.anyio
async def test_list_servers_can_filter_by_status():
    server = await main.register_server(
        ServerIn(name="api", host="httpbin.org", port=443)
    )
    server.status = "UP"

    assert await main.list_servers(status="DOWN") == []
    assert await main.list_servers(status="UP") == [server]


@pytest.mark.anyio
async def test_delete_server_removes_existing_server():
    server = await main.register_server(
        ServerIn(name="api", host="httpbin.org", port=443)
    )

    await main.delete_server(server.id)

    assert await main.list_servers() == []


@pytest.mark.anyio
async def test_get_missing_server_returns_404():
    with pytest.raises(HTTPException) as exc_info:
        await main.get_server(999)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Server not found"


class FakeWebSocket:
    def __init__(self):
        self.accepted = False
        self.payload = None

    async def accept(self):
        self.accepted = True

    async def send_json(self, payload):
        self.payload = payload
        raise WebSocketDisconnect()


@pytest.mark.anyio
async def test_websocket_metrics():
    websocket = FakeWebSocket()

    await main.websocket_metrics(websocket)

    assert websocket.accepted is True
    assert {"cpu_percent", "memory_percent", "disk_percent"} <= websocket.payload.keys()
