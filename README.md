# IELTS Vocabulary Tutor

## Features

- Chat-based IELTS vocabulary practice
- Amazon Bedrock Converse API integration
- Definitions, Russian translations, collocations, examples, and exercises
- In-memory browser conversation history
- Responsive vanilla HTML/CSS/JavaScript interface

## Architecture

The browser sends the current message and previous conversation to a FastAPI backend. The backend adds the IELTS tutor system prompt and calls Amazon Bedrock Runtime with the Converse API. No authentication or database is used.

## Requirements

- Python 3.11+
- An AWS account with access to an available Amazon Bedrock model
- AWS credentials configured through the standard AWS credential chain or local environment variables

## AWS Bedrock setup

1. Create or use an AWS account.
2. Open Amazon Bedrock in the AWS console.
3. Select an available model and confirm it supports the Converse API.
4. Make sure the model is available in your chosen AWS region.
5. Request or enable model access if required for that model and region.
6. Configure local credentials with `aws configure` or another standard boto3 credential provider. Alternatively, set the optional long-lived key variables described below. Never commit credentials to Git.
7. Copy `.env.example` to `.env`.
8. Set `AWS_REGION` and `BEDROCK_MODEL_ID` in `.env`. If using a Bedrock API key, put it in `AWS_BEARER_TOKEN_BEDROCK`; do not put the key in `BEDROCK_MODEL_ID`.

## IAM permissions

The runtime identity needs only model invocation permission. Scope the resource to the selected model where supported:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": "bedrock:Converse",
    "Resource": "arn:aws:bedrock:REGION::foundation-model/MODEL_ID"
  }]
}
```

Some model providers or account configurations may require additional Bedrock permissions. Do not use `AdministratorAccess`.

## Environment variables

| Variable | Description |
| --- | --- |
| `AWS_REGION` | AWS region where the Bedrock model is enabled |
| `BEDROCK_MODEL_ID` | ID of the selected Bedrock model |
| `AWS_BEARER_TOKEN_BEDROCK` | Optional Bedrock API key; use instead of access key variables |
| `MAX_TOKENS` | Optional response token limit; defaults to `1200` |
| `AWS_ACCESS_KEY_ID` | Optional IAM access key ID for local static credentials |
| `AWS_SECRET_ACCESS_KEY` | Optional IAM secret access key for local static credentials |
| `AWS_SESSION_TOKEN` | Optional temporary-session token; leave unset for long-lived keys |

For local development, you can put long-lived keys in `.env`:

```dotenv
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
```

The application uses these values only when both key variables are present. If
they are absent, boto3 uses its normal credential chain. Long-lived keys are
less safe than short-lived credentials; use a narrowly scoped IAM user or role,
rotate the keys regularly, and never put them in source code, screenshots, or
committed files.

## Installation

```bash
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running locally

Terminal 1:

```bash
cd backend
source .venv/bin/activate
uvicorn main:app --reload --port 8000
```

Terminal 2:

```bash
cd frontend
python3 -m http.server 5500
```

Open http://localhost:5500. The frontend uses CORS to communicate with the backend.

## API endpoints

- `GET /api/health` checks whether required environment variables are configured.
- `POST /api/chat` accepts `{"message":"What does detrimental mean?","history":[]}` and returns `reply`, `word`, and `suggestions`.
- `POST /api/reset` returns a successful reset acknowledgement. Browser history is cleared by starting a new page session.

Example:

```bash
curl -X POST http://localhost:8000/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"What does detrimental mean?","history":[]}'
```

## Project structure

```text
backend/
  main.py
  bedrock.py
  prompts.py
  config.py
  requirements.txt
frontend/
  index.html
  style.css
  app.js
.env.example
.gitignore
README.md
```

## Troubleshooting

- `not_configured`: copy `.env.example` to `.env` and set both required variables.
- Access or model errors: check the selected region, model access, model ID, and IAM `bedrock:Converse` permission.
- If `/api/chat` returns `502`, read the Uvicorn terminal output. It logs the Bedrock error code and message while the API hides internal AWS details from the browser.
- Browser connection errors: ensure both servers are running and open the frontend through `http://localhost:5500`, not a different port.
- Credential errors: verify the AWS CLI profile or other boto3 credential provider works locally.

## Next steps

Future versions:

1. User accounts
2. PostgreSQL/DynamoDB
3. Vocabulary progress tracking
4. Spaced repetition
5. IELTS Speaking mode
6. Voice input
7. Speech-to-text
8. Pronunciation feedback
9. Personal IELTS study plan
10. Bedrock Knowledge Bases
11. Production deployment on AWS
