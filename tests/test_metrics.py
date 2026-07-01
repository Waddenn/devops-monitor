from api.metrics import get_system_metrics


def test_get_system_metrics_contains_expected_fields():
    metrics = get_system_metrics()

    assert set(metrics) == {"cpu_percent", "memory_percent", "disk_percent"}
    for value in metrics.values():
        assert 0 <= value <= 100
