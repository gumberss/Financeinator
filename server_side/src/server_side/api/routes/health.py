from fastapi import APIRouter

from server_side.services.health_service import get_health_status

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
def health() -> dict[str, str]:
    return get_health_status()
