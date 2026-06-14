import asyncio
import json
from json import JSONDecodeError
from typing import Any

import google.generativeai as genai
from fastapi import HTTPException, status
from google.api_core import exceptions as google_exceptions
from pydantic import ValidationError

from app.config import get_settings
from app.models import StudyMaterial
from app.utils.retry import RetryableError, retry_async


MOCK_STUDY_MATERIAL = StudyMaterial(
    summary="This is a mock summary generated for local testing.",
    flashcards=[
        {
            "question": "What is DevOps?",
            "answer": "DevOps is a practice that combines software development and IT operations.",
        }
    ],
    mcqs=[
        {
            "question": "What does CI/CD stand for?",
            "options": [
                "Code Integration / Code Deployment",
                "Continuous Integration / Continuous Deployment",
                "Cloud Integration / Cloud Delivery",
                "Container Integration / Container Deployment",
            ],
            "answer": "Continuous Integration / Continuous Deployment",
        }
    ],
    revision_points=[
        "DevOps improves collaboration.",
        "Docker helps containerize applications.",
        "CI/CD automates testing and deployment.",
    ],
)


def build_prompt(notes: str) -> str:
    """
    Build Gemini prompt safely.

    Important:
    We use doubled braces {{ }} inside the f-string because the prompt contains
    JSON examples. This avoids Python formatting errors.
    """
    return f"""You are an academic study assistant. Convert the following notes into structured study material.

Return only valid JSON. Do not include markdown, explanations, or code fences.

The JSON must have exactly these keys:
summary, flashcards, mcqs, revision_points.

Return the JSON in this exact structure:

{{
  "summary": "short summary here",
  "flashcards": [
    {{
      "question": "question here",
      "answer": "answer here"
    }}
  ],
  "mcqs": [
    {{
      "question": "question here",
      "options": ["option A", "option B", "option C", "option D"],
      "answer": "correct option here"
    }}
  ],
  "revision_points": ["point 1", "point 2", "point 3"]
}}

Notes:
{notes}
"""


def _strip_json_code_fence(text: str) -> str:
    """
    Gemini sometimes returns JSON inside markdown code fences.
    This function removes ```json and ``` if present.
    """
    cleaned = text.strip()

    if cleaned.startswith("```"):
        lines = cleaned.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        cleaned = "\n".join(lines).strip()

    if cleaned.lower().startswith("json"):
        cleaned = cleaned[4:].strip()

    return cleaned


def _is_retryable_google_error(error: Exception) -> bool:
    """
    These are temporary errors where retrying makes sense.
    """
    return isinstance(
        error,
        (
            google_exceptions.TooManyRequests,
            google_exceptions.InternalServerError,
            google_exceptions.BadGateway,
            google_exceptions.ServiceUnavailable,
            google_exceptions.GatewayTimeout,
            google_exceptions.DeadlineExceeded,
            google_exceptions.RetryError,
        ),
    )


async def generate_study_material(notes: str) -> StudyMaterial:
    settings = get_settings()

    # If Gemini key is missing, return mock data for local testing.
    if not settings.gemini_api_key:
        return MOCK_STUDY_MATERIAL

    genai.configure(api_key=settings.gemini_api_key)

    model = genai.GenerativeModel("gemini-2.5-flash")
    prompt = build_prompt(notes)

    async def call_gemini() -> StudyMaterial:
        try:
            response = await asyncio.to_thread(
                model.generate_content,
                prompt,
                generation_config={"response_mime_type": "application/json"},
                request_options={"timeout": 30},
            )

            response_text = getattr(response, "text", "") or ""

            if not response_text.strip():
                raise RetryableError("Gemini returned an empty response")

            cleaned_response = _strip_json_code_fence(response_text)
            parsed: Any = json.loads(cleaned_response)

            return StudyMaterial.model_validate(parsed)

        except (JSONDecodeError, ValidationError) as error:
            raise RetryableError("Gemini returned invalid JSON") from error

        except Exception as error:
            if _is_retryable_google_error(error):
                raise RetryableError("Gemini request failed temporarily") from error

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unexpected AI service error: {str(error)}",
            ) from error

    try:
        return await retry_async(call_gemini)

    except RetryableError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI service could not generate valid study material. Please try again.",
        ) from error