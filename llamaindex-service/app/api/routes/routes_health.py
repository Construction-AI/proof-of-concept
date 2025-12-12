from fastapi import APIRouter, status
from fastapi.responses import Response

router = APIRouter()

@router.get("")
def route_get_health():
    return Response(
        status_code=status.HTTP_200_OK
    )