import json
import logging
from typing import Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from config import (
    AWS_ACCESS_KEY_ID,
    AWS_REGION,
    AWS_SECRET_ACCESS_KEY,
    AWS_SESSION_TOKEN,
    BEDROCK_MODEL_ID,
    MAX_TOKENS,
    TEMPERATURE,
)
from prompts import SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class BedrockServiceError(Exception):
    """Raised when Bedrock cannot complete a vocabulary response."""


def _client():
    credentials = {}
    if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
        credentials = {
            "aws_access_key_id": AWS_ACCESS_KEY_ID,
            "aws_secret_access_key": AWS_SECRET_ACCESS_KEY,
        }
        if AWS_SESSION_TOKEN:
            credentials["aws_session_token"] = AWS_SESSION_TOKEN
    return boto3.client("bedrock-runtime", region_name=AWS_REGION, **credentials)


def _extract_text(response: dict[str, Any]) -> str:
    try:
        content = response["output"]["message"]["content"]
        return "".join(part.get("text", "") for part in content).strip()
    except (KeyError, TypeError) as error:
        raise BedrockServiceError("Bedrock returned an unexpected response.") from error


def _parse_model_response(text: str) -> dict[str, Any]:
    cleaned_text = text.strip()
    if cleaned_text.startswith("```") and cleaned_text.endswith("```"):
        cleaned_text = cleaned_text[3:-3].strip()
        if cleaned_text.startswith("json"):
            cleaned_text = cleaned_text[4:].strip()

    decoder = json.JSONDecoder()
    objects: list[dict[str, Any]] = []
    position = 0
    try:
        while position < len(cleaned_text):
            while position < len(cleaned_text) and cleaned_text[position].isspace():
                position += 1
            if position >= len(cleaned_text):
                break
            parsed, end = decoder.raw_decode(cleaned_text, position)
            if not isinstance(parsed, dict) or not isinstance(parsed.get("reply"), str):
                return {"reply": text, "word": None, "suggestions": []}
            objects.append(parsed)
            position = end
    except json.JSONDecodeError:
        return {"reply": text, "word": None, "suggestions": []}

    if not objects:
        return {"reply": text, "word": None, "suggestions": []}

    replies = [item["reply"].strip() for item in objects if item["reply"].strip()]
    suggestions: list[str] = []
    for item in objects:
        item_suggestions = item.get("suggestions", [])
        if isinstance(item_suggestions, list):
            suggestions.extend(
                suggestion
                for suggestion in item_suggestions
                if isinstance(suggestion, str)
            )
    words = [
        item["word"]
        for item in objects
        if isinstance(item.get("word"), str) and item["word"].strip()
    ]
    return {
        "reply": "\n\n".join(replies),
        "word": words[0] if words else None,
        "suggestions": suggestions,
    }


def generate_reply(message: str, history: list[dict[str, str]]) -> dict[str, Any]:
    messages = [
        {"role": item["role"], "content": [{"text": item["content"]}]}
        for item in history
        if item["role"] in {"user", "assistant"} and item["content"].strip()
    ]
    messages.append({"role": "user", "content": [{"text": message}]})

    try:
        response = _client().converse(
            modelId=BEDROCK_MODEL_ID,
            system=[{"text": SYSTEM_PROMPT}],
            messages=messages,
            inferenceConfig={"temperature": TEMPERATURE, "maxTokens": MAX_TOKENS},
        )
        return _parse_model_response(_extract_text(response))
    except ClientError as error:
        error_code = error.response.get("Error", {}).get("Code", "Unknown")
        error_message = error.response.get("Error", {}).get("Message", str(error))
        logger.error("Bedrock request failed (%s): %s", error_code, error_message)
        raise BedrockServiceError("The vocabulary tutor is temporarily unavailable.") from error
    except BotoCoreError as error:
        logger.error("Bedrock request failed: %s", error)
        raise BedrockServiceError("The vocabulary tutor is temporarily unavailable.") from error
