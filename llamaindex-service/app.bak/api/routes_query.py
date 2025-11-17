from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.services.query_service import (
    ChatRequest,
    ChatResponse,
    process_chat_query,
    process_chat_query_stream
)

router = APIRouter()


@router.post("/query", response_model=ChatResponse)
async def chat_with_documents(req: ChatRequest):
    """
    Free-form chat with project documents.
    
    Send a natural language query and get an AI-generated response
    based on the indexed documents for the specified project.
    
    Args:
        req: ChatRequest containing project_id, query, and optional history
        
    Returns:
        ChatResponse with answer and source references
        
    Example:
        ```
        POST /chat/query
        {
            "project_id": "my-project",
            "query": "What are the main findings about customer satisfaction?",
            "top_k": 5,
            "history": [
                {"role": "user", "content": "Tell me about the survey"},
                {"role": "assistant", "content": "The survey covered 500 customers..."}
            ]
        }
        ```
    """
    return await process_chat_query(req)


@router.post("/stream")
async def chat_with_documents_stream(req: ChatRequest):
    """
    Free-form chat with streaming response.
    
    Same as /chat/query but streams the response token-by-token
    for a more interactive experience.
    
    Returns:
        StreamingResponse with text/event-stream content type
        
    Example:
        ```
        POST /chat/stream
        {
            "project_id": "my-project",
            "query": "Summarize the key points from the report",
            "top_k": 5
        }
        ```
    """
    return StreamingResponse(
        process_chat_query_stream(req),
        media_type="text/event-stream"
    )