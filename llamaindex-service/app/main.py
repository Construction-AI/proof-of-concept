from fastapi import FastAPI
from app.api import (
    routes_health,
    routes_index,
    routes_query,
    routes_field_extraction,
    routes_schema
)

def create_app() -> FastAPI:
    app = FastAPI(
        title="LlamaIndex Service", 
        description="Document ingestion, indexing and querying API using LlamaIndex and Qdrant.",
        version="1.0.0"
        )

    # Register routes
    app.include_router(routes_health.router, tags=["System"])
    app.include_router(routes_index.router, prefix="/index", tags=["Indexing"])
    app.include_router(routes_query.router, prefix="/query", tags=['Query'])
    app.include_router(routes_field_extraction.router, prefix="/fill_field", tags=["Field Extraction"])
    app.include_router(routes_schema.router, prefix="/schema", tags=["Schema"])

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)