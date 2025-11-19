from fastapi import HTTPException
from llama_index.core.postprocessor import MetadataReplacementPostProcessor
from pydantic import BaseModel, Field
from typing import List, Optional

from app.services.index_service import retrievers
from app.core.llama_settings import Settings


WINDOW_POST = MetadataReplacementPostProcessor(target_metadata_key="window")


# Request/Response Models
class ChatMessage(BaseModel):
    role: str = Field(..., description="Role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    project_id: str = Field(..., description="Project identifier")
    query: str = Field(..., description="User's question or query")
    top_k: int = Field(default=5, description="Number of context chunks to retrieve")
    history: Optional[List[ChatMessage]] = Field(default=None, description="Conversation history")


class SourceReference(BaseModel):
    file_name: Optional[str] = None
    page_label: Optional[str] = None
    score: float
    excerpt: str


class ChatResponse(BaseModel):
    response: str = Field(..., description="AI-generated response")
    sources: List[SourceReference] = Field(default_factory=list, description="Source references")
    retrieved_chunks: int = Field(..., description="Number of chunks used")


def build_context_snippets(nodes, max_chars_per_snip=800):
    """Build context from retrieved nodes."""
    def _snip(txt: str, n=max_chars_per_snip):
        return (txt[:n] + "..." if txt and len(txt) > n else txt)

    parts = []
    for i, sn in enumerate(nodes, start=1):
        node = sn.node if hasattr(sn, "node") else sn
        meta = node.metadata or {}
        file_name = meta.get("file_name", "unknown")
        page_label = meta.get("source", "unknown")
        parts.append(
            f"[{i}] file={file_name} page={page_label}\n{_snip(node.get_content())}"
        )
        
    return "\n\n---\n\n".join(parts)


def build_chat_prompt(query: str, context: str, history: Optional[List[ChatMessage]] = None) -> str:
    """Build a chat prompt with context and optional history."""
    
    prompt_parts = [
        "You are a helpful AI assistant that answers questions based on provided documents.",
        "",
        "INSTRUCTIONS:",
        "- Answer the user's question using ONLY the information from the Context below",
        "- Be conversational and natural in your responses",
        "- If the answer isn't in the context, say so clearly",
        "- Cite specific details when relevant",
        "- If multiple perspectives exist in the documents, acknowledge them",
        "- Keep responses concise but complete",
        "",
    ]
    
    # Add conversation history if provided
    if history and len(history) > 0:
        prompt_parts.append("CONVERSATION HISTORY:")
        for msg in history[-6:]:  # Last 6 messages to keep context manageable
            role_label = "User" if msg.role == "user" else "Assistant"
            prompt_parts.append(f"{role_label}: {msg.content}")
        prompt_parts.append("")
    
    # Add context
    prompt_parts.extend([
        "CONTEXT FROM DOCUMENTS:",
        context,
        "",
        f"USER QUESTION: {query}",
        "",
        "ANSWER:"
    ])
    
    return "\n".join(prompt_parts)


async def process_chat_query(req: ChatRequest) -> ChatResponse:
    """Process a free-form chat query against project documents."""
    
    pid = req.project_id
    
    # Validate project exists
    if pid not in retrievers:
        raise HTTPException(
            status_code=400, 
            detail=f"No index for project_id='{pid}'. Create it with /index."
        )
    
    try:
        # 1) Retrieve relevant chunks
        fusion = retrievers[pid]
        nodes = await fusion.aretrieve(req.query)
        
        # Apply sentence-window replacement for better context
        windowed_nodes = WINDOW_POST.postprocess_nodes(nodes, query_str=req.query)
        
        # 2) Build context from top nodes
        top_nodes = windowed_nodes[:req.top_k]
        context = build_context_snippets(top_nodes, max_chars_per_snip=1200)
        
        # 3) Build chat prompt
        prompt = build_chat_prompt(req.query, context, req.history)
        
        # 4) Generate response using LLM
        llm = Settings.llm
        response = await llm.acomplete(prompt)
        answer = str(response)
        
        # 5) Build source references
        sources = []
        for sn in top_nodes:
            node = sn.node if hasattr(sn, "node") else sn
            meta = node.metadata or {}
            content = node.get_content() or ""
            excerpt = content if len(content) <= 500 else (content[:500] + "...")
            
            sources.append(SourceReference(
                file_name=meta.get("file_name"),
                page_label=meta.get("source"),
                score=sn.score,
                excerpt=excerpt
            ))
        
        return ChatResponse(
            response=answer.strip(),
            sources=sources,
            retrieved_chunks=len(top_nodes)
        )
        
    except Exception as e:
        print(f"Error in chat query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Optional: Streaming version for real-time responses
async def process_chat_query_stream(req: ChatRequest):
    """Process chat query with streaming response."""
    
    pid = req.project_id
    
    if pid not in retrievers:
        raise HTTPException(
            status_code=400,
            detail=f"No index for project_id='{pid}'. Create it with /index."
        )
    
    try:
        # Retrieve and build context (same as above)
        fusion = retrievers[pid]
        nodes = await fusion.aretrieve(req.query)
        windowed_nodes = WINDOW_POST.postprocess_nodes(nodes, query_str=req.query)
        top_nodes = windowed_nodes[:req.top_k]
        context = build_context_snippets(top_nodes, max_chars_per_snip=1200)
        
        # Build prompt
        prompt = build_chat_prompt(req.query, context, req.history)
        
        # Stream response
        llm = Settings.llm
        async for chunk in await llm.astream_complete(prompt):
            yield chunk.delta
            
    except Exception as e:
        print(f"Error in streaming chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))