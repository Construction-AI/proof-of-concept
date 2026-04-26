import os
import httpx
from fastapi import APIRouter, status
from typing import Any

router = APIRouter()

@router.get("", status_code=status.HTTP_200_OK)
async def get_health() -> dict[str, Any]:
    # Pobieramy adresy z sieci Dockera (wartości domyślne na wypadek ich braku)
    qdrant_url = os.getenv("QDRANT_URL", "http://qdrant:6333")
    minio_url = os.getenv("MINIO_ENDPOINT", "minio:9000")
    minio_health_url = f"http://{minio_url}/minio/health/live"

    services = {
        "api": "up",
        "qdrant": "down",
        "minio": "down"
    }

    # Asynchroniczne sprawdzanie serwisów (timeout 2 sekundy, żeby nie blokować API)
    async with httpx.AsyncClient(timeout=2.0) as client:
        try:
            res_qdrant = await client.get(qdrant_url)
            if res_qdrant.status_code == 200:
                services["qdrant"] = "up"
        except Exception:
            pass

        try:
            res_minio = await client.get(minio_health_url)
            if res_minio.status_code == 200:
                services["minio"] = "up"
        except Exception:
            pass
    overall_status = "ok" if all(v == "up" for v in services.values()) else "degraded"

    return {
        "status": overall_status,
        "services": services
    }