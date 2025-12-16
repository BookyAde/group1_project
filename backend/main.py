# 📄 backend/main.py - FIXED WITH CORS

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.core.config import settings, initialize_supabase_clients
from backend.routers import auth, data

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.API_VERSION,
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs"
)

# ✅ CRITICAL: Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if hasattr(settings, 'CORS_ORIGINS') else ["http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Startup Event: Initialize Supabase clients
@app.on_event("startup")
async def startup_event():
    initialize_supabase_clients()

# Include API Routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(data.router, prefix="/api/v1")

# Health Check Endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": settings.PROJECT_NAME,
        "version": settings.API_VERSION,
        "cors_origins": settings.CORS_ORIGINS if hasattr(settings, 'CORS_ORIGINS') else ["http://localhost:8501"]
    }

@app.get("/")
async def root():
    return {
        "message": "Data Platform API is running",
        "docs": "/api/v1/docs",
        "health": "/health",
        "cors_enabled": True
    }