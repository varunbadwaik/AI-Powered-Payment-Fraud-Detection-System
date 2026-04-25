"""
FastAPI application entrypoint for the AI-Powered Payment Fraud Detection System.

Features:
    - CORS middleware for Streamlit frontend integration
    - Lifespan management for model preloading
    - Structured request logging
    - OpenAPI documentation with metadata

Security Notes (PCI-DSS Awareness):
    - Requirement 1: Network segmentation → handled at infrastructure level.
    - Requirement 6: Secure coding → Pydantic validation, no SQL injection via parameterized queries.
    - Requirement 10: Logging → all predictions logged with structured JSON.
    - This system processes ONLY synthetic data — no real cardholder data.
"""

import sys
import os
import time
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

# Ensure project root is in path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.api.routes import router
from backend.api.websockets import ws_manager
from backend.database.connection import close_database
from models.inference import model_manager
from utils.constants import API_VERSION
from utils.config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.

    Startup:
        - Load ML models into memory for fast inference.
    Shutdown:
        - Close database connections gracefully.
    """
    # ---- Startup ----
    logger.info("Starting Fraud Detection API...")
    try:
        model_manager.load_models()
        logger.info("Models loaded successfully")
    except FileNotFoundError:
        logger.warning(
            "Model artifacts not found. "
            "Run 'python run.py --mode train' to train models first. "
            "API will start in degraded mode."
        )
    except Exception as e:
        logger.error(f"Failed to load models: {e}")

    yield

    # ---- Shutdown ----
    logger.info("Shutting down API...")
    await close_database()
    logger.info("API shutdown complete")


# ---- Application factory ----
app = FastAPI(
    title="AI-Powered Payment Fraud Detection API",
    description=(
        "Real-time fraud detection system using ensemble machine learning. "
        "Provides risk scoring, transaction analysis, and explainable AI "
        "for financial transaction monitoring."
    ),
    version=API_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---- CORS Middleware ----
# Allow React frontend to communicate with the API
_frontend_url = os.environ.get("FRONTEND_URL", "")
_allowed_origins = [
    "http://localhost:5173",       # Vite dev server
    "http://127.0.0.1:5173",
    "http://localhost:8501",       # Streamlit fallback
    f"http://localhost:{settings.STREAMLIT_PORT}",
]
if _frontend_url:
    _allowed_origins.append(_frontend_url)
else:
    _allowed_origins.append("*")  # Development convenience only

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---- Request logging middleware ----
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests with timing information."""
    start = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start) * 1000

    logger.info(
        f"{request.method} {request.url.path} -> {response.status_code} "
        f"({duration_ms:.1f}ms)"
    )

    # Add timing header for monitoring
    response.headers["X-Response-Time-Ms"] = f"{duration_ms:.1f}"

    return response


# ---- Exception Handlers ----
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic API validation errors."""
    logger.warning(f"API Validation Error [{request.method} {request.url.path}]: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "message": "The provided input data is invalid.",
            "details": exc.errors()
        },
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all for unexpected internal errors."""
    logger.error(f"Unhandled Server Error [{request.method} {request.url.path}]: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred processing your request."
        },
    )


# ---- Include API routes ----
app.include_router(router, prefix="/api/v1")


# ---- Root endpoint ----
@app.get("/", tags=["System"])
async def root():
    """API root — provides navigation info."""
    return {
        "service": "AI-Powered Payment Fraud Detection API",
        "version": API_VERSION,
        "docs": "/docs",
        "health": "/api/v1/health",
        "predict": "/api/v1/predict",
        "websocket": "/ws/predictions",
    }


# ---- WebSocket endpoint for real-time streaming ----
@app.websocket("/ws/predictions")
async def websocket_endpoint(websocket: WebSocket):
    """Real-time prediction streaming via WebSocket."""
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive, listen for client messages
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
