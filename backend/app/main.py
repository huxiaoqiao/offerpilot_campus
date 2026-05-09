"""FastAPI application entry point for OfferPilot Campus."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import create_all_tables
from app.routers import (
    dashboard,
    hr_simulator,
    interview,
    jobs,
    match,
    profile,
    resume,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: create all database tables. Shutdown: cleanup."""
    await create_all_tables()
    yield


app = FastAPI(
    title="OfferPilot Campus",
    description="AI-powered campus recruitment assistant - backend API",
    version="0.1.0",
    lifespan=lifespan,
)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Register routers ---
app.include_router(profile.router)
app.include_router(jobs.router)
app.include_router(match.router)
app.include_router(resume.router)
app.include_router(hr_simulator.router)
app.include_router(interview.router)
app.include_router(dashboard.router)


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "version": "0.1.0"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug,
    )
