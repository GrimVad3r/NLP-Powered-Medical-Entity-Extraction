"""
FastAPI application setup with NLP endpoints.

BRANCH-6: REST API
Author: Boris (Claude Code)
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from contextlib import asynccontextmanager

from src.core.config import get_settings
from src.core.logger import get_logger
from src.nlp.message_processor import MedicalMessageProcessor
from src.nlp.medical_ner import MedicalEntity

logger = get_logger(__name__)
settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model when the app starts
    logger.info("Loading NLP models...")
    app.state.processor = MedicalMessageProcessor()
    yield
    # Clean up the ML model and release resources on shutdown
    logger.info("Cleaning up NLP models...")
    del app.state.processor

# ============================================================================
# Request/Response Models
# ============================================================================

class MedicalEntityResponse(BaseModel):
    """Medical entity response model."""
    text: str
    entity_type: str
    start_char: int
    end_char: int
    confidence: float
    normalized: Optional[str] = None

    class Config:
                model_config = {
                    "json_schema_extra": {
                        "examples": [
                            {
                                "text": "Amoxicillin",
                                "entity_type": "MEDICATION",
                                # ...
                            }
                        ]
                    }
                }


class ProcessMessageRequest(BaseModel):
    """Request to process a medical message."""
    text: str = Field(..., min_length=1, max_length=5000, description="Medical text to process")

    class Config:
        schema_extra = {
            "example": {
                "text": "Malaria treatment with artemether 500mg twice daily for 7 days. Price: 50 ETB"
            }
        }


class ProcessMessageResponse(BaseModel):
    """Response from message processing."""
    text: str
    is_medical: bool
    medical_confidence: float
    entities: List[MedicalEntityResponse]
    quality_score: float
    processing_status: str
    error_message: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "text": "Malaria treatment with artemether",
                "is_medical": True,
                "medical_confidence": 0.95,
                "entities": [
                    {
                        "text": "Malaria",
                        "entity_type": "CONDITION",
                        "start_char": 0,
                        "end_char": 7,
                        "confidence": 0.92
                    }
                ],
                "quality_score": 0.85,
                "processing_status": "success",
                "error_message": None
            }
        }


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    nlp_available: bool
    database_connected: bool


class ModelInfoResponse(BaseModel):
    """NLP model information."""
    ner_model: str
    classifier_model: str
    nlp_version: str
    gpu_available: bool


# ============================================================================
# Create FastAPI Application
# ============================================================================

def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.

    Returns:
        FastAPI application instance
    """
    app = FastAPI(
        title=settings.app_name,
        description="Advanced NLP-Powered Medical Data Pipeline",
        version=settings.app_version,
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
        lifespan=lifespan
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ====================================================================
    # Health Check Endpoints
    # ====================================================================

    @app.get("/health", tags=["Health"], response_model=HealthResponse)
    async def health_check() -> HealthResponse:
        """
        Check application health status.

        Returns:
            Health status information
        """
        return HealthResponse(
            status="healthy",
            version=settings.app_version,
            nlp_available=True,
            database_connected=True,
        )

    @app.get("/api/v1/health", tags=["Health"], response_model=HealthResponse)
    async def api_health_check() -> HealthResponse:
        """
        Check API health status.

        Returns:
            Health status information
        """
        return HealthResponse(
            status="healthy",
            version=settings.app_version,
            nlp_available=True,
            database_connected=True,
        )

    # ====================================================================
    # NLP Processing Endpoints
    # ====================================================================

    @app.post(
        "/api/v1/nlp/process-message",
        response_model=ProcessMessageResponse,
        tags=["NLP"],
        summary="Process Medical Message"
    )
    async def process_message(request: ProcessMessageRequest) -> ProcessMessageResponse:
        """
        Process a medical message through complete NLP pipeline.

        This endpoint:
        1. Classifies text as medical or non-medical
        2. Extracts medical entities (medications, dosages, etc.)
        3. Links entities to knowledge bases
        4. Calculates quality score

        Args:
            request: ProcessMessageRequest with text

        Returns:
            ProcessMessageResponse with processing results

        Example:
            ```python
            curl -X POST http://localhost:8000/api/v1/nlp/process-message \\
              -H "Content-Type: application/json" \\
              -d '{"text": "Malaria treatment with artemether 500mg"}'
            ```

        Raises:
            HTTPException: If processing fails
        """
        try:
            logger.info(f"Processing message: {request.text[:100]}...")

            result = app.state.processor.process_message(request.text)

            if result.processing_status == "error":
                raise HTTPException(
                    status_code=500,
                    detail=f"Processing error: {result.error_message}"
                )

            return ProcessMessageResponse(
                text=result.text,
                is_medical=result.is_medical,
                medical_confidence=result.medical_confidence,
                entities=[
                    MedicalEntityResponse(
                        text=e.text,
                        entity_type=e.entity_type,
                        start_char=e.start_char,
                        end_char=e.end_char,
                        confidence=e.confidence,
                        normalized=e.normalized,
                    )
                    for e in result.entities
                ],
                quality_score=result.quality_score,
                processing_status=result.processing_status,
                error_message=result.error_message,
            )

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get(
        "/api/v1/nlp/extract-entities",
        response_model=List[MedicalEntityResponse],
        tags=["NLP"],
        summary="Extract Entities"
    )
    async def extract_entities(
        text: str = Query(..., min_length=1, max_length=5000, description="Text to process"),
        min_confidence: float = Query(0.5, ge=0.0, le=1.0, description="Minimum confidence score")
    ) -> List[MedicalEntityResponse]:
        """
        Extract medical entities from text.

        Args:
            text: Input text
            min_confidence: Minimum confidence threshold

        Returns:
            List of extracted entities
        """
        try:
            logger.debug(f"Extracting entities from text")

            result = processor.process_message(text)

            # Filter by confidence
            filtered_entities = [
                e for e in result.entities
                if e.confidence >= min_confidence
            ]

            return [
                MedicalEntityResponse(
                    text=e.text,
                    entity_type=e.entity_type,
                    start_char=e.start_char,
                    end_char=e.end_char,
                    confidence=e.confidence,
                    normalized=e.normalized,
                )
                for e in filtered_entities
            ]

        except Exception as e:
            logger.error(f"Error extracting entities: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get(
        "/api/v1/nlp/classify-text",
        tags=["NLP"],
        summary="Classify Text"
    )
    async def classify_text(
        text: str = Query(..., min_length=1, max_length=5000, description="Text to classify")
    ) -> dict:
        """
        Classify text as medical or non-medical.

        Args:
            text: Input text

        Returns:
            Classification result with confidence
        """
        try:
            logger.debug(f"Classifying text")

            result = processor.process_message(text)

            return {
                "text": text[:100],
                "is_medical": result.is_medical,
                "confidence": result.medical_confidence,
            }

        except Exception as e:
            logger.error(f"Error classifying text: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get(
        "/api/v1/nlp/models",
        response_model=ModelInfoResponse,
        tags=["NLP"],
        summary="Get Model Info"
    )
    async def get_models() -> ModelInfoResponse:
        """
        Get information about loaded NLP models.

        Returns:
            Model information
        """
        return ModelInfoResponse(
            ner_model="en_core_sci_md",
            classifier_model="distilbert-base-uncased-finetuned-sst-2-english",
            nlp_version="1.0.0",
            gpu_available=settings.nlp_use_gpu,
        )

    # ====================================================================
    # Batch Processing Endpoint
    # ====================================================================

    @app.post(
        "/api/v1/nlp/batch-process",
        response_model=List[ProcessMessageResponse],
        tags=["NLP"],
        summary="Batch Process Messages"
    )
    async def batch_process_messages(
        requests: List[ProcessMessageRequest]
    ) -> List[ProcessMessageResponse]:
        """
        Process multiple messages in batch.

        Args:
            requests: List of ProcessMessageRequest objects

        Returns:
            List of ProcessMessageResponse objects
        """
        try:
            logger.info(f"Batch processing {len(requests)} messages")

            responses = []
            for request in requests:
                result = processor.process_message(request.text)
                responses.append(
                    ProcessMessageResponse(
                        text=result.text,
                        is_medical=result.is_medical,
                        medical_confidence=result.medical_confidence,
                        entities=[
                            MedicalEntityResponse(
                                text=e.text,
                                entity_type=e.entity_type,
                                start_char=e.start_char,
                                end_char=e.end_char,
                                confidence=e.confidence,
                                normalized=e.normalized,
                            )
                            for e in result.entities
                        ],
                        quality_score=result.quality_score,
                        processing_status=result.processing_status,
                        error_message=result.error_message,
                    )
                )

            return responses

        except Exception as e:
            logger.error(f"Error batch processing: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    # ====================================================================
    # Root Endpoint
    # ====================================================================

    @app.get("/", tags=["Info"], summary="API Information")
    async def root() -> dict:
        """Get API information."""
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "description": "Medical Intelligence Platform",
            "docs": "/api/docs",
            "health": "/health",
        }

    logger.info("FastAPI application created successfully")
    return app


# ============================================================================
# Create Application Instance
# ============================================================================

app = create_app()


# ============================================================================
# Run Application
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        workers=settings.api_workers,
        log_level=settings.log_level.lower(),
    )