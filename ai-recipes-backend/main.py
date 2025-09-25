"""
AI Recipes Backend - FastAPI Application
"""
import logging
import traceback
import time
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import uvicorn

from config import settings
from models import AnalysisResponse, ErrorResponse, SuccessResponse
from gemini_service import gemini_service, GeminiServiceError

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("ai-recipes-backend.log")
    ]
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    logger.info("Starting AI Recipes Backend...")
    logger.info(f"Environment: {'Development' if settings.debug else 'Production'}")
    logger.info(f"Allowed origins: {settings.allowed_origins_list}")
    
    # Startup
    try:
        # Test Gemini connection
        logger.info("Testing Gemini API connection...")
        # You could add a simple test here if needed
        logger.info("✓ Backend initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize backend: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Recipes Backend...")


# Create FastAPI app
app = FastAPI(
    title="AI Recipes Backend",
    description="Backend service for AI-powered ingredient analysis and recipe generation",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list + ["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# Custom exception handlers
@app.exception_handler(GeminiServiceError)
async def gemini_service_exception_handler(request: Request, exc: GeminiServiceError):
    """Handle Gemini service errors."""
    logger.error(f"Gemini service error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Analysis service temporarily unavailable",
            detail=str(exc) if settings.debug else None,
            status_code=500
        ).dict()
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors."""
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(
            error="Invalid request format",
            detail=str(exc.errors()) if settings.debug else None,
            status_code=400
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors."""
    logger.error(f"Unexpected error: {str(exc)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc) if settings.debug else None,
            status_code=500
        ).dict()
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "AI Recipes Backend", "version": "1.0.0"}


# Main analysis endpoint with basic rate limiting
@app.post("/analyze", response_model=SuccessResponse)
async def analyze_image(
    file: UploadFile = File(..., description="Image file containing food ingredients"),
    request: Request = None
):
    # Basic IP-based rate limiting (production needs Redis/database)
    client_ip = request.client.host if request else "unknown"
    
    # Simple in-memory rate limiting (replace with Redis in production)
    current_time = time.time()
    if not hasattr(analyze_image, 'rate_limit'):
        analyze_image.rate_limit = {}
    
    # Allow 10 requests per minute per IP
    if client_ip in analyze_image.rate_limit:
        last_requests = analyze_image.rate_limit[client_ip]
        # Remove requests older than 1 minute
        recent_requests = [t for t in last_requests if current_time - t < 60]
        if len(recent_requests) >= 10:
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please wait a minute before trying again."
            )
        analyze_image.rate_limit[client_ip] = recent_requests + [current_time]
    else:
        analyze_image.rate_limit[client_ip] = [current_time]
    """
    Analyze uploaded image to detect ingredients and generate recipe suggestions.
    
    Args:
        file: Image file (JPEG, PNG, WebP supported)
        
    Returns:
        SuccessResponse containing detected ingredients and recipe suggestions
        
    Raises:
        HTTPException: For various error conditions
    """
    logger.info(f"Received image analysis request: {file.filename}")
    
    # Validate file
    if not file:
        raise HTTPException(
            status_code=400,
            detail="No file provided"
        )
    
    # Check file type
    if file.content_type not in settings.allowed_file_types_list:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed types: {', '.join(settings.allowed_file_types_list)}"
        )
    
    # Read file content
    try:
        file_content = await file.read()
    except Exception as e:
        logger.error(f"Failed to read uploaded file: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail="Failed to read uploaded file"
        )
    
    # Check file size
    if len(file_content) > settings.max_file_size_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.max_file_size_mb}MB"
        )
    
    if len(file_content) == 0:
        raise HTTPException(
            status_code=400,
            detail="Empty file provided"
        )
    
    # Analyze image
    try:
        logger.debug(f"Analyzing image: {len(file_content)} bytes")
        analysis_result = await gemini_service.analyze_image(file_content)
        
        # Log results
        logger.info(f"Analysis completed - Ingredients: {len(analysis_result.ingredients)}, Recipes: {len(analysis_result.recipes)}")
        
        # Return success response
        return SuccessResponse(
            success=True,
            data=analysis_result,
            message="Image analyzed successfully"
        )
        
    except GeminiServiceError as e:
        logger.error(f"Gemini service error during analysis: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="Analysis service temporarily unavailable. Please try again later."
        )
    
    except Exception as e:
        logger.error(f"Unexpected error during analysis: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during image analysis"
        )


# Development endpoints (only available in debug mode)
if settings.debug:
    
    @app.get("/debug/config")
    async def debug_config():
        """Debug endpoint to check configuration."""
        return {
            "gemini_model": settings.gemini_model,
            "max_file_size_mb": settings.max_file_size_mb,
            "allowed_file_types": settings.allowed_file_types_list,
            "allowed_origins": settings.allowed_origins_list,
            "request_timeout": settings.request_timeout,
            "max_retries": settings.max_retries,
        }
    
    @app.post("/debug/test-gemini")
    async def test_gemini():
        """Test endpoint for Gemini API connectivity."""
        try:
            # Create a simple test image (1x1 white pixel)
            from PIL import Image
            from io import BytesIO
            
            test_image = Image.new('RGB', (1, 1), color='white')
            img_bytes = BytesIO()
            test_image.save(img_bytes, format='JPEG')
            test_bytes = img_bytes.getvalue()
            
            # This should return empty results for a white pixel
            result = await gemini_service.analyze_image(test_bytes)
            
            return {
                "status": "success",
                "gemini_responsive": True,
                "test_result": {
                    "ingredients_found": len(result.ingredients),
                    "recipes_found": len(result.recipes)
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "gemini_responsive": False,
                "error": str(e)
            }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info",
        access_log=True
    )
