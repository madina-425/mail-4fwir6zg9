from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from bedrock import BedrockServiceError, generate_reply
from config import missing_settings

app = FastAPI(title="IELTS Vocabulary Tutor")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500", "null"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class HistoryMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=12000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    history: list[HistoryMessage] = Field(default_factory=list, max_length=50)


@app.get("/api/health")
def health() -> dict[str, object]:
    missing = missing_settings()
    return {"status": "ok" if not missing else "not_configured", "missing": missing}


@app.post("/api/chat")
def chat(request: ChatRequest) -> dict[str, object]:
    message = request.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    missing = missing_settings()
    if missing:
        raise HTTPException(
            status_code=503,
            detail="The server is not configured. Set the required environment variables.",
        )

    try:
        return generate_reply(
            message,
            [item.model_dump() for item in request.history],
        )
    except BedrockServiceError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error


@app.post("/api/reset")
def reset() -> dict[str, str]:
    return {"status": "ok"}
