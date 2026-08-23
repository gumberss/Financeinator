from server_side.services.health_service import get_health_status


def test_get_health_status_returns_ok() -> None:
    assert get_health_status() == {"status": "ok"}
