"""
Main FastAPI application entry point.
Sets up middleware, routers, and lifecycle events.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db, close_db
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-powered technical interview evaluation platform",
)

# Configure CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """
    Application startup event handler.
    Initializes database connections and performs health checks.
    """
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    await init_db()
    logger.info("Application startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown event handler.
    Closes database connections and cleans up resources.
    """
    logger.info("Shutting down application")
    await close_db()
    logger.info("Application shutdown complete")


@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {
        "message": "AI Interview Platform API",
        "version": settings.VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for deployment platforms."""
    return {"status": "healthy"}


# Register routers
from app.routers import auth_router, interview_router, answer_router, report_router

app.include_router(auth_router.router)
app.include_router(interview_router.router)
app.include_router(answer_router.router)
app.include_router(report_router.router)
