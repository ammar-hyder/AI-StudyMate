import json
import os

import boto3
from botocore.exceptions import BotoCoreError, ClientError


ses_client = boto3.client("ses")


def _response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def _format_study_material(study_material):
    lines = [
        "Your AI StudyMate study material is ready.",
        "",
        "Summary",
        study_material.get("summary", "No summary provided."),
        "",
        "Flashcards",
    ]

    for index, card in enumerate(study_material.get("flashcards", []), start=1):
        lines.append(f"{index}. Q: {card.get('question', '')}")
        lines.append(f"   A: {card.get('answer', '')}")

    lines.extend(["", "MCQs"])
    for index, mcq in enumerate(study_material.get("mcqs", []), start=1):
        lines.append(f"{index}. {mcq.get('question', '')}")
        for option in mcq.get("options", []):
            lines.append(f"   - {option}")
        lines.append(f"   Answer: {mcq.get('answer', '')}")

    lines.extend(["", "Key Revision Points"])
    for point in study_material.get("revision_points", []):
        lines.append(f"- {point}")

    return "\n".join(lines)


def lambda_handler(event, context):
    # SES sender email must be verified.
    # SES sandbox accounts may also require recipient email verification.
    # The Lambda IAM role must allow ses:SendEmail.
    sender_email = os.environ.get("SENDER_EMAIL")
    if not sender_email:
        return _response(500, {"success": False, "message": "SENDER_EMAIL is not configured"})

    try:
        body = event.get("body", event)
        if isinstance(body, str):
            body = json.loads(body)

        recipient = body["email"]
        study_material = body["study_material"]
        email_body = _format_study_material(study_material)

        ses_client.send_email(
            Source=sender_email,
            Destination={"ToAddresses": [recipient]},
            Message={
                "Subject": {"Data": "Your AI StudyMate Study Material"},
                "Body": {"Text": {"Data": email_body}},
            },
        )

        return _response(200, {"success": True, "message": "Email sent successfully"})
    except (KeyError, json.JSONDecodeError) as error:
        return _response(400, {"success": False, "message": f"Invalid request: {error}"})
    except (BotoCoreError, ClientError) as error:
        return _response(502, {"success": False, "message": f"SES error: {error}"})
    except Exception as error:
        return _response(500, {"success": False, "message": f"Unexpected error: {error}"})
