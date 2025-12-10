import os
import logging
from dotenv import load_dotenv
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .core.shared.exceptions_handler import setup_exception_handlers
from .core.db import init_db
from src.api.v1.router import router
from src.api.v1.reports.routes import router as reports_router

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Async context manager for FastAPI application."""
    logger.info("Starting up...")

    # Initialize database
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise

    logger.info("Hi Tai Business Plan Dashboard API startup completed")

    yield

    logger.info("Shutting down...")
    logger.info("Hi Tai Business Plan Dashboard API shutdown completed")

# Create FastAPI app
app = FastAPI(
    title="Hi Tai Business Plan Dashboard API",
    description=(
        f"""
        API for reporting and visualising 
        business plan data from Google Spreadsheets
        """)
)

# Setup global exception handlers
setup_exception_handlers(app)
logger.info("Exception handlers configured")

@app.get("/")
async def root():
    return {
        "message": "Welcome to Hi Tai Business Plan Dashboard API",
        "docs": "/docs" if os.getenv("ENV", "development") == "development" else "Documentation disabled in production",
        "health": "/health",
        "dashboard": "/dashboard"
    }

# Health check and utility endpoints
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": "Hi Tai Business Plan Dashboard API",
        "version": "1.0.0",
        "environment": os.getenv("ENV", "development")
    }

# Routers
app.include_router(router)
app.include_router(reports_router)

# Import dashboard to mount Dash app
import dashboard  # noqa: F401

# Error handling verification endpoint (development only)
if os.getenv("ENV", "development") == "development":

    @app.get("/test-exceptions", tags=["Development"])
    async def test_exceptions(exception_type: str = "validation"):
        """Test different exception types (development only)."""
        from .core.shared.exceptions import (
            ValidationError, NotFoundError, BadRequestError, 
            UnauthorizedError, InternalServerError
        )
        
        if exception_type == "validation":
            raise ValidationError(
                detail="Test validation error",
                context={"test": True}
            )
        elif exception_type == "notfound":
            raise NotFoundError(
                detail="Test not found error",
                context={"test": True}
            )
        elif exception_type == "badrequest":
            raise BadRequestError(
                detail="Test bad request error",
                context={"test": True}
            )
        elif exception_type == "unauthorized":
            raise UnauthorizedError(
                detail="Test unauthorized error",
                context={"test": True}
            )
        elif exception_type == "internal":
            raise InternalServerError(
                detail="Test internal server error",
                context={"test": True}
            )
        else:
            raise Exception("Test generic exception")
        
        return {"message": "This should not be reached"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('src.main:app', host='0.0.0.0', port=8000, reload=True)
