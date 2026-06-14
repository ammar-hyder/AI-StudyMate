# AWS Deployment Notes

## 1. Push Images to Amazon ECR

Create two ECR repositories:

- `ai-studymate-backend`
- `ai-studymate-frontend`

Build, tag, and push the Docker images from GitHub Actions or your local machine.

## 2. Deploy Backend on ECS Fargate

Use the sample `aws/ecs-task-definition.json` as a starting point.

Recommended ECS service settings:

- Launch type: Fargate
- Desired count: 2
- Backend container port: 8000
- Network mode: awsvpc
- Public IP: disabled if using private subnets with NAT
- Task role permissions: allow `lambda:InvokeFunction` for the email Lambda

## 3. Application Load Balancer

Create an internet-facing Application Load Balancer for HTTP traffic.

- Listener: HTTP port 80
- Target group type: IP
- Target group protocol: HTTP
- Target group port: 8000
- Health check path: `/health`
- Expected health response: HTTP 200

Security groups:

- ALB security group allows inbound HTTP 80 from the internet.
- ECS service security group allows inbound traffic on port 8000 only from the ALB security group.

## 4. Lambda and SES

Deploy `aws/lambda/email_lambda.py` as a Python Lambda function.

Environment variable:

- `SENDER_EMAIL`: verified SES sender address

IAM permissions:

- Lambda execution role needs `ses:SendEmail`.
- ECS task role needs `lambda:InvokeFunction` for this Lambda.

SES notes:

- The sender email must be verified.
- In the SES sandbox, recipient emails must also be verified.
- Move SES out of sandbox for production use.

## 5. Frontend Deployment Options

Choose one:

- Deploy the frontend as a separate ECS service behind the ALB.
- Host the built frontend on S3 and CloudFront.
- Run the frontend container on EC2.

Set `VITE_API_BASE_URL` to the backend ALB URL during frontend build.

## 6. Runtime Configuration

Backend environment variables:

- `GEMINI_API_KEY`
- `EMAIL_LAMBDA_FUNCTION_NAME`
- `AWS_REGION`
- `CORS_ORIGINS`

Store sensitive values in GitHub Secrets, ECS task secrets, or AWS Secrets Manager.
