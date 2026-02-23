from fastapi import APIRouter, status

router = APIRouter()

@router.get("", status_code=status.HTTP_200_OK)
def get_health():
    return "ok"