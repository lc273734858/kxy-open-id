import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from app.utils.json_response import JSONResponse
from fastapi.staticfiles import StaticFiles
import os

from app.routers import auth, database, segment
from app.services.scanner_service import ScannerService
from app.redis_client import RedisClient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

scanner_task = None


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    global scanner_task

    logger.info("Starting up...")

    try:
        await RedisClient.get_instance()
        logger.info("Redis connection established")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")

    scanner_task = asyncio.create_task(ScannerService.start_background_scanner())
    logger.info("Background scanner task started")

    yield

    logger.info("Shutting down...")

    if scanner_task:
        scanner_task.cancel()
        try:
            await scanner_task
        except asyncio.CancelledError:
            logger.info("Background scanner task cancelled")

    try:
        await RedisClient.close()
        logger.info("Redis connection closed")
    except Exception as e:
        logger.error(f"Error closing Redis connection: {e}")


app = FastAPI(
    title="KXY ID Generator Service",
    description="Distributed ID segment allocation service with multi-database support",
    version="1.0.0",
    lifespan=lifespan,
    default_response_class=JSONResponse
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(database.router)
app.include_router(segment.router)


@app.exception_handler(Exception)
async def global_exception_handler(_request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "msg": "Internal Server Error",
            "data": None
        }
    )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "code": 0,
        "msg": "KXY ID Generator Service is running",
        "data": {
            "version": "1.0.0",
            "status": "healthy"
        }
    }


frontend_dist_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
frontend_index_path = os.path.join(frontend_dist_path, "index.html")

if os.path.exists(frontend_dist_path):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist_path, "assets")), name="static")
    logger.info(f"Serving frontend static assets from {frontend_dist_path}/assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Serve frontend for all non-API routes"""
        if full_path.startswith("api/"):
            return JSONResponse(status_code=404, content={"code": 404, "msg": "Not found", "data": None})

        file_path = os.path.join(frontend_dist_path, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)

        if os.path.exists(frontend_index_path):
            return FileResponse(frontend_index_path)

        return JSONResponse(status_code=404, content={"code": 404, "msg": "Frontend not found", "data": None})
else:
    logger.warning(f"Frontend dist directory not found at {frontend_dist_path}. Please build the frontend first.")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=5801, reload=True)
