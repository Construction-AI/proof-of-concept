from fastapi import APIRouter, HTTPException
from app.infra.instances_qdrant import get_qdrant_client_wrapper

router = APIRouter()

@router.post("")
async def create_point():
    try:
        wrapper = get_qdrant_client_wrapper()
        point = wrapper.create_point(
            1,
            [0.9, 0.1, 0.1],
            "straz",
            False,
            "BIOZ",
            "madeupurl"
        )

        if not await wrapper.check_collection_exists("documents"):
            await wrapper.create_collection("documents", vector_size=3)

        await wrapper.insert_vectors(
            collection_name="documents",
            vectors=[point],

        )
        return "ok"

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))