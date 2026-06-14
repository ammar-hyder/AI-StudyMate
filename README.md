# AI StudyMate

AI StudyMate is a semester-level DevOps project that lets a student paste notes, generate AI study material with Google Gemini, and send the generated result to email through an AWS Lambda function and Amazon SES.

## Features

- React + Vite frontend with a clean student-friendly UI
- FastAPI backend with automatic Swagger docs
- Gemini API integration using `google-generativeai`
- Local mock AI response when `GEMINI_API_KEY` is not configured
- AWS Lambda email integration through `boto3`
- Local mock email response when `EMAIL_LAMBDA_FUNCTION_NAME` is not configured
- Exponential backoff retry logic for Gemini and Lambda
- Dockerfiles and Docker Compose
- AWS ECS Fargate, ECR, ALB, Lambda, and SES deployment templates
- GitHub Actions CI/CD pipeline
- Health endpoint for load balancer checks

## Architecture

```text
User
  ↓
React Frontend
  ↓
Application Load Balancer
  ↓
ECS Fargate Backend Container
  ↓
Gemini API

Email flow:

FastAPI Backend
  ↓
AWS Lambda Email Function
  ↓
Amazon SES
  ↓
User Email
```

## Tech Stack

- Frontend: React, Vite, Axios, CSS
- Backend: FastAPI, Pydantic, google-generativeai, boto3
- DevOps: Docker, Docker Compose, GitHub Actions
- AWS: ECR, ECS Fargate, Application Load Balancer, Lambda, SES, CloudWatch Logs

## Folder Structure

```text
ai-studymate/
  backend/
    app/
      __init__.py
      main.py
      config.py
      models.py
      services/
        __init__.py
        ai_service.py
        email_service.py
      utils/
        __init__.py
        retry.py
    tests/
      test_health.py
    requirements.txt
    Dockerfile
    .env.example
  frontend/
    src/
      App.jsx
      api.js
      components/
        NotesForm.jsx
        ResultsDisplay.jsx
        LoadingSpinner.jsx
      styles.css
    package.json
    vite.config.js
    Dockerfile
    nginx.conf
    .env.example
  aws/
    lambda/
      email_lambda.py
    ecs-task-definition.json
    deployment-notes.md
  .github/
    workflows/
      ci-cd.yml
  docker-compose.yml
  README.md
  .gitignore
```

## Local Setup

Backend:

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Open the frontend at `http://localhost:3000`. The backend runs at `http://localhost:8000`.

## Docker Setup

From the project root:

```bash
docker-compose up --build
```

Frontend: `http://localhost:3000`

Backend: `http://localhost:8000`

Swagger docs: `http://localhost:8000/docs`

## Environment Variables

Backend `.env`:

```env
GEMINI_API_KEY=your_gemini_api_key_here
EMAIL_LAMBDA_FUNCTION_NAME=ai-studymate-email-lambda
AWS_REGION=us-east-1
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

Frontend `.env`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

If `GEMINI_API_KEY` is missing, the backend returns a mock study material response. If `EMAIL_LAMBDA_FUNCTION_NAME` is missing, `/send-email` returns a mock success response.

## API Documentation

`GET /`

```json
{ "message": "AI StudyMate backend is running" }
```

`GET /health`

```json
{ "status": "healthy", "service": "ai-studymate-backend" }
```

`POST /generate`

```json
{ "notes": "student notes here" }
```

`POST /send-email`

```json
{
  "email": "student@example.com",
  "study_material": {
    "summary": "...",
    "flashcards": [],
    "mcqs": [],
    "revision_points": []
  }
}
```

## CI/CD Pipeline

The GitHub Actions workflow in `.github/workflows/ci-cd.yml`:

1. Checks out code
2. Installs backend dependencies
3. Runs backend tests
4. Installs frontend dependencies
5. Builds the frontend
6. Builds backend and frontend Docker images
7. Logs in to AWS ECR
8. Pushes both images to ECR
9. Deploys the backend image to ECS

Required GitHub Secrets:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`
- `ECR_BACKEND_REPOSITORY`
- `ECR_FRONTEND_REPOSITORY`
- `ECS_CLUSTER`
- `ECS_SERVICE`
- `ECS_TASK_DEFINITION`
- `GEMINI_API_KEY`
- `EMAIL_LAMBDA_FUNCTION_NAME`
- `VITE_API_BASE_URL`

Expected values:

```text
AWS_REGION=eu-north-1
ECR_BACKEND_REPOSITORY=ai-studymate-backend
ECR_FRONTEND_REPOSITORY=ai-studymate-frontend
ECS_CLUSTER=ai-studymate-cluster
ECS_SERVICE=ai-studymate-backend-service
ECS_TASK_DEFINITION=aws/ecs-task-definition.json
EMAIL_LAMBDA_FUNCTION_NAME=ai-studymate-email-lambda
VITE_API_BASE_URL=http://YOUR_ALB_DNS
```

Store the real Gemini key only in the `GEMINI_API_KEY` GitHub Secret. Do not commit API keys or AWS access keys to task definition files, `.env` examples, or documentation.

## AWS Deployment

Use `aws/deployment-notes.md` for the full deployment checklist.

Backend recommended setup:

- Push backend image to Amazon ECR
- Run backend on ECS Fargate
- Attach ECS service to an Application Load Balancer
- Set target group health check path to `/health`
- Set ECS desired count to `2`
- Allow inbound HTTP 80 to the ALB
- Allow ECS inbound port 8000 only from the ALB security group

Frontend deployment options:

- Separate ECS service behind ALB
- S3 + CloudFront static hosting
- Frontend container on EC2

## Lambda Email Function

`aws/lambda/email_lambda.py` receives an email address and study material, formats a readable plain-text email, and sends it through Amazon SES.

Lambda environment variable:

```env
SENDER_EMAIL=verified-sender@example.com
```

Important SES notes:

- Sender email must be verified.
- SES sandbox may require recipient email verification.
- Lambda IAM role must allow `ses:SendEmail`.
- ECS task role must allow `lambda:InvokeFunction`.

## Load Balancer Readiness

The backend is stateless, uses environment-based configuration, stores no local files, exposes `/health`, and runs on container port `8000`. This makes it suitable for multiple ECS tasks behind an ALB.

## Retry Logic

Retry utility: `backend/app/utils/retry.py`

Rules:

- Maximum retries: `3`
- Initial delay: `1` second
- Backoff multiplier: `2`
- Total attempts: `4`

Retries are used for Gemini API calls and AWS Lambda invocation. The app retries temporary network, timeout, rate-limit, 500-level, and invalid Gemini JSON failures. It does not retry invalid user input or missing local configuration that intentionally triggers mock mode.

## Tests

```bash
cd backend
pytest
```

Tests cover:

- `/health` returns healthy
- `/generate` rejects empty notes
- `/generate` rejects notes shorter than 20 characters

## Screenshots

Add screenshots after running the app:

- `docs/screenshots/home-page.png`
- `docs/screenshots/generated-results.png`
- `docs/screenshots/email-success.png`

## Future Improvements

- Store generation history in DynamoDB or PostgreSQL
- Add user authentication
- Add PDF export
- Add frontend unit tests
- Use AWS Secrets Manager for runtime secrets
- Deploy frontend to S3 and CloudFront
- Add Terraform or AWS CDK infrastructure as code
