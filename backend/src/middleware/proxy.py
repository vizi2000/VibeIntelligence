"""
Proxy middleware to handle reverse proxy headers
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import logging

logger = logging.getLogger(__name__)

class ProxyHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle X-Forwarded headers from reverse proxy
    """
    
    async def dispatch(self, request: Request, call_next):
        # Handle X-Forwarded headers
        forwarded_proto = request.headers.get("X-Forwarded-Proto", "http")
        forwarded_host = request.headers.get("X-Forwarded-Host", request.headers.get("Host", "localhost"))
        
        # Override the URL scheme and host
        request.scope["scheme"] = forwarded_proto
        
        # Set the proper host
        if ":" in forwarded_host:
            host, port = forwarded_host.split(":", 1)
            request.scope["server"] = (host, int(port))
        else:
            default_port = 443 if forwarded_proto == "https" else 80
            request.scope["server"] = (forwarded_host, default_port)
        
        response = await call_next(request)
        return response