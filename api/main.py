import asyncio
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect

from api.auth import verify_api_key
from api.metrics import get_system_metrics
from api.models import Server, ServerIn, ServerOut
from api.poller import poll_server, run_poll_loop


_store: dict[int, Server] = {}
_counter = 0
_stop_event: asyncio.Event | None = None
_poll_task: asyncio.Task[None] | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _stop_event, _poll_task
    _stop_event = asyncio.Event()
    _poll_task = asyncio.create_task(run_poll_loop(_store, stop_event=_stop_event))
    try:
        yield
    finally:
        _stop_event.set()
        if _poll_task:
            await _poll_task


app = FastAPI(
    title="DevOps Monitoring API",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/metrics")
async def metrics() -> dict[str, float]:
    return get_system_metrics()


@app.websocket("/ws/metrics")
async def websocket_metrics(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        while True:
            await websocket.send_json(get_system_metrics())
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        return


@app.post(
    "/servers",
    response_model=ServerOut,
    status_code=201,
    dependencies=[Depends(verify_api_key)],
)
async def register_server(server: ServerIn) -> Server:
    global _counter
    _counter += 1
    record = Server(
        id=_counter,
        name=server.name,
        host=server.host,
        port=server.port,
        tags=server.tags,
    )
    _store[record.id] = record
    return record


@app.get("/servers", response_model=list[ServerOut])
async def list_servers(status: str | None = None) -> list[Server]:
    servers = list(_store.values())
    if status is not None:
        return [server for server in servers if server.status == status]
    return servers


@app.get("/servers/{server_id}", response_model=ServerOut)
async def get_server(server_id: int) -> Server:
    if server_id not in _store:
        raise HTTPException(status_code=404, detail="Server not found")
    return _store[server_id]


@app.delete(
    "/servers/{server_id}",
    status_code=204,
    dependencies=[Depends(verify_api_key)],
)
async def delete_server(server_id: int) -> None:
    if server_id not in _store:
        raise HTTPException(status_code=404, detail="Server not found")
    del _store[server_id]


@app.post("/servers/{server_id}/check", response_model=ServerOut)
async def trigger_health_check(server_id: int) -> Server:
    if server_id not in _store:
        raise HTTPException(status_code=404, detail="Server not found")
    return await poll_server(_store[server_id])
