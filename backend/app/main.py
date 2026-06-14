from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.models import EmailRequest, EmailResponse, GenerateRequest, StudyMaterial
from app.services.ai_service import generate_study_material
from app.services.email_service import send_study_material_email


settings = get_settings()

app = FastAPI(
    title="AI StudyMate API",
    description="FastAPI backend for generating study material with Gemini and sending it by email.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected server error occurred."},
    )


@app.get("/")
async def root():
    return {"message": "AI StudyMate backend is running"}


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "ai-studymate-backend"}


@app.post("/generate", response_model=StudyMaterial)
async def generate(request: GenerateRequest):
    return await generate_study_material(request.notes)


@app.post("/send-email", response_model=EmailResponse)
async def send_email(request: EmailRequest):
    result = await send_study_material_email(
        str(request.email),
        request.study_material,
    )
    return EmailResponse(
        success=bool(result.get("success", True)),
        message=result.get("message", "Email sent successfully"),
    )
