# Main FastAPI application
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
import uuid

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.core.db import init_db
from app.api.v1 import entities, properties, scores, health, verification


# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info(f"Starting {settings.app_name} in {settings.environment} mode")
    
    # Initialize database (only in development)
    if settings.is_development:
        init_db()
        logger.info("Database initialized")
    
    # Log configuration
    logger.info(f"API v1 prefix: {settings.api_v1_prefix}")
    logger.info(f"Log level: {settings.log_level}")
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {settings.app_name}")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Chain Of Record - Entity, Property, and Risk Intelligence Platform",
    version="1.0.0",
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
    openapi_url="/openapi.json" if settings.is_development else None,
    lifespan=lifespan
)


# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.is_development else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if settings.is_production:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*.chainofrecord.com", "chainofrecord.com"]
    )


# Request ID middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add unique request ID for tracing."""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = str(process_time)
    
    # Log request
    logger.info(
        f"{request.method} {request.url.path} - {response.status_code}",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "process_time": process_time
        }
    )
    
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unexpected errors."""
    request_id = getattr(request.state, "request_id", "unknown")
    
    logger.error(
        f"Unhandled exception: {str(exc)}",
        extra={"request_id": request_id, "path": request.url.path},
        exc_info=True
    )
    
    if settings.is_development:
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "request_id": request_id,
                "error": str(exc) if settings.is_development else None
            }
        )
    else:
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error", 
                "request_id": request_id
            }
        )


# Include API routers
app.include_router(health.router, prefix=settings.api_v1_prefix)
app.include_router(entities.router, prefix=settings.api_v1_prefix)
app.include_router(properties.router, prefix=settings.api_v1_prefix)
app.include_router(scores.router, prefix=settings.api_v1_prefix)
app.include_router(verification.router, prefix=settings.api_v1_prefix)


# Root endpoint
@app.get("/")
def root():
    """Root endpoint with basic API information."""
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "environment": settings.environment,
        "docs_url": "/docs" if settings.is_development else None,
        "api_prefix": settings.api_v1_prefix,
        "status": "operational"
    }


# API info endpoint
@app.get("/info")
def api_info():
    """API information and available endpoints."""
    endpoints = [
        {"path": "/", "methods": ["GET"], "description": "Root endpoint"},
        {"path": "/health", "methods": ["GET"], "description": "Basic health check"},
        {"path": "/health/detailed", "methods": ["GET"], "description": "Detailed health check"},
        {"path": "/stats", "methods": ["GET"], "description": "System statistics"},
        {"path": "/api/v1/entities", "methods": ["GET", "POST"], "description": "Entity management"},
        {"path": "/api/v1/properties", "methods": ["GET", "POST"], "description": "Property management"},
        {"path": "/api/v1/scores", "methods": ["GET", "POST"], "description": "Risk scoring"},
        {"path": "/api/v1/verification", "methods": ["GET", "POST"], "description": "KYC verification workflow"},
    ]
    
    return {
        "api_name": settings.app_name,
        "version": "1.0.0",
        "environment": settings.environment,
        "endpoints": endpoints
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.is_development,
        log_level=settings.log_level.lower()
    )