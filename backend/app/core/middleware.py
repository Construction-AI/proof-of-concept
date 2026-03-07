import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logger import trace_id_var

class TraceIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next): # type: ignore TODO: Add type
        # 1. Generujemy unikalne ID dla tego żądania
        trace_id = str(uuid.uuid4())
        
        # 2. Ustawiamy w kontekście
        token = trace_id_var.set(trace_id)
        
        # 3. Puszczamy request dalej w głąb aplikacji
        response = await call_next(request)
        
        # 4. Zwracamy trace_id w nagłówkach (przydatne do debugowania na frontendzie)
        response.headers["X-Trace-ID"] = trace_id
        
        # 5. Czyścimy kontekst
        trace_id_var.reset(token)
        
        return response