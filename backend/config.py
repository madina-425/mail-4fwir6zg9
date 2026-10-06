import os

from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "").strip()
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "").strip()
AWS_BEARER_TOKEN_BEDROCK = os.getenv("AWS_BEARER_TOKEN_BEDROCK", "").strip()
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "").strip()
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "").strip()
AWS_SESSION_TOKEN = os.getenv("AWS_SESSION_TOKEN", "").strip()
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1200"))
TEMPERATURE = 0.3


def missing_settings() -> list[str]:
    """Return required settings that have not been configured."""
    missing = []
    if not AWS_REGION:
        missing.append("AWS_REGION")
    if not BEDROCK_MODEL_ID:
        missing.append("BEDROCK_MODEL_ID")
    elif BEDROCK_MODEL_ID.startswith("bedrock-api-key-"):
        missing.append(
            "BEDROCK_MODEL_ID must be a model ID; put the Bedrock API key in "
            "AWS_BEARER_TOKEN_BEDROCK"
        )
    if bool(AWS_ACCESS_KEY_ID) != bool(AWS_SECRET_ACCESS_KEY):
        missing.append("AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY must be set together")
    return missing
