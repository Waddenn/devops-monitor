import psutil


def get_system_metrics() -> dict[str, float]:
    """Return a non-blocking snapshot of system CPU, memory, and disk usage."""

    return {
        "cpu_percent": float(psutil.cpu_percent(interval=None)),
        "memory_percent": float(psutil.virtual_memory().percent),
        "disk_percent": float(psutil.disk_usage("/").percent),
    }
