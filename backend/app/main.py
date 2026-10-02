"""FastAPI application entry point."""

import logging
from typing import Any, Dict

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import settings
from .middleware import RateLimitMiddleware, SecurityHeadersMiddleware
from .schemas import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    LoginRequest,
    SummaryRequest,
    SummaryResponse,
    TokenResponse,
)
from .security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from .services.gemini_service import GeminiService

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO)
)
logger = logging.getLogger("ai_studio_hub")

app = FastAPI(title=settings.app_name, version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add security middleware
app.add_middleware(RateLimitMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

# Demo user store for development
# In production, use a database with hashed passwords
USER_DB: Dict[str, str] = {"admin": hash_password("ChangeMe123!")}

# Initialize Gemini service
try:
    gemini_service = GeminiService()
except ValueError:
    gemini_service = None
    logger.warning("Google API key not configured")


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(
        app_name=settings.app_name, environment=settings.app_env, status="ok"
    )


@app.post("/api/auth/token", response_model=TokenResponse)
async def create_token(payload: LoginRequest) -> TokenResponse:
    """Authenticate user and return JWT token."""
    stored_hash = USER_DB.get(payload.username)
    if not stored_hash or not verify_password(payload.password, stored_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    token = create_access_token(payload.username)
    return TokenResponse(access_token=token, token_type="bearer")


@app.post("/api/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest, user: dict = Depends(get_current_user)
) -> ChatResponse:
    """Chat with Gemini AI."""
    if gemini_service is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google API key missing",
        )

    response_text = await gemini_service.generate(
        prompt=request.prompt,
        system_prompt=request.system_prompt,
        max_tokens=request.max_tokens,
    )
    return ChatResponse(
        response=response_text,
        model=settings.google_model,
        tokens_used=request.max_tokens,
    )


@app.post("/api/summarize", response_model=SummaryResponse)
async def summarize(
    request: SummaryRequest, user: dict = Depends(get_current_user)
) -> SummaryResponse:
    """Summarize text using Gemini."""
    if gemini_service is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google API key missing",
        )

    summary = await gemini_service.summarize(request.text, style=request.summary_style)
    return SummaryResponse(summary=summary, model=settings.google_model)


@app.exception_handler(429)
async def rate_limit_handler(_: Any, __: Any) -> JSONResponse:
    """Handle rate limit errors."""
    return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_env == "development",
    )
