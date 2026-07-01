import asyncio
import logging
import time
from collections.abc import MutableMapping

import httpx

from api.models import Server

logger = logging.getLogger(__name__)


async def poll_server(
    server: Server,
    timeout: float = 5.0,
    degraded_threshold_ms: float = 500.0,
) -> Server:
    """Check a server /health endpoint and update its status."""

    try:
        started_at = time.perf_counter()
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(f"{server.base_url()}/health")
        elapsed_ms = (time.perf_counter() - started_at) * 1000
        if response.status_code != 200:
            server.status = "DEGRADED"
        elif elapsed_ms > degraded_threshold_ms:
            server.status = "DEGRADED"
        else:
            server.status = "UP"
    except (httpx.HTTPError, OSError):
        server.status = "DOWN"
    return server


async def run_poll_loop(
    store: MutableMapping[int, Server],
    interval_seconds: float = 10.0,
    stop_event: asyncio.Event | None = None,
) -> None:
    """Poll all registered servers until cancelled or stopped."""

    while stop_event is None or not stop_event.is_set():
        servers = list(store.values())
        if servers:
            logger.info("Polling %s server(s)", len(servers))
            await asyncio.gather(*(poll_server(server) for server in servers))
        try:
            if stop_event is None:
                await asyncio.sleep(interval_seconds)
            else:
                await asyncio.wait_for(stop_event.wait(), timeout=interval_seconds)
        except asyncio.TimeoutError:
            continue
