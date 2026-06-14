import asyncio
import json

import boto3
from botocore.exceptions import BotoCoreError, ClientError, ConnectTimeoutError, ReadTimeoutError
from fastapi import HTTPException, status

from app.config import get_settings
from app.models import StudyMaterial
from app.utils.retry import RetryableError, retry_async


def _is_retryable_aws_error(error: Exception) -> bool:
    if isinstance(error, (ConnectTimeoutError, ReadTimeoutError, BotoCoreError)):
        return True
    if isinstance(error, ClientError):
        status_code = error.response.get("ResponseMetadata", {}).get("HTTPStatusCode", 0)
        error_code = error.response.get("Error", {}).get("Code", "")
        return status_code == 429 or status_code >= 500 or error_code in {
            "TooManyRequestsException",
            "ThrottlingException",
            "ServiceException",
        }
    return False


async def send_study_material_email(email: str, study_material: StudyMaterial) -> dict:
    settings = get_settings()

    if not settings.email_lambda_function_name:
        return {
            "success": True,
            "message": "Mock email sent successfully. Configure EMAIL_LAMBDA_FUNCTION_NAME to invoke Lambda.",
        }

    payload = {
        "email": email,
        "study_material": study_material.model_dump(),
    }

    async def invoke_lambda() -> dict:
        try:
            client = boto3.client("lambda", region_name=settings.aws_region)
            response = await asyncio.to_thread(
                client.invoke,
                FunctionName=settings.email_lambda_function_name,
                InvocationType="RequestResponse",
                Payload=json.dumps(payload).encode("utf-8"),
            )
            body = json.loads(response["Payload"].read().decode("utf-8") or "{}")
            if response.get("FunctionError"):
                raise RetryableError("Email Lambda returned a function error")

            if isinstance(body, dict) and "body" in body:
                status_code = body.get("statusCode", 200)
                lambda_body = body.get("body") or "{}"
                parsed_body = json.loads(lambda_body) if isinstance(lambda_body, str) else lambda_body
                if status_code >= 500:
                    raise RetryableError("Email Lambda returned a temporary server error")
                if status_code >= 400:
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail=parsed_body.get("message", "Email Lambda rejected the request."),
                    )
                return parsed_body

            return body if isinstance(body, dict) else {"success": True, "message": "Email sent successfully"}
        except Exception as error:
            if isinstance(error, HTTPException):
                raise
            if isinstance(error, RetryableError) or _is_retryable_aws_error(error):
                raise RetryableError("Lambda invocation failed temporarily") from error
            if isinstance(error, (ClientError, BotoCoreError)):
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Email service returned an AWS error.",
                ) from error
            raise

    try:
        return await retry_async(invoke_lambda)
    except RetryableError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Email service is temporarily unavailable. Please try again.",
        ) from error
