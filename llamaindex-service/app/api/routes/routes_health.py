from fastapi import APIRouter

router = APIRouter()

@router.get("")
def route_get_health():
    return "ok"