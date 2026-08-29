from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path
from uuid import uuid4
import os
import logging
import threading

from ai_service import AIService
from character_conversation_service import CharacterConversationService


class ChatRequest(BaseModel):
    query: str


class InternalRespondRequest(BaseModel):
    character_id: str
    character_name: str
    prompt_key: str
    model_name: str | None = None
    conversation_type: str
    conversation_id: str
    context: str | None = ""
    message: str


class ExperienceReviewRequest(BaseModel):
    status: str
    score: int | None = None
    comment: str = ""


app = FastAPI()
ai_service = AIService()
character_service = CharacterConversationService(ai_service.registry)
logger = logging.getLogger("uvicorn.error")


def _warmup_character_model():
    try:
        character_service.warmup()
        logger.info("Character model warmup completed")
    except Exception as error:
        logger.warning("Character model warmup failed: %s", error)


@app.on_event("startup")
def start_character_model_warmup():
    if os.getenv("AI_WARMUP", "true").lower() in ("1", "true", "yes", "on"):
        threading.Thread(target=_warmup_character_model, daemon=True).start()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory=Path(__file__).resolve().parent / "static"), name="static")


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    logger.warning("Invalid request for %s: %s", request.url.path, exc.errors())
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.post("/chat-stream")
def chat_stream(req: ChatRequest):
    experience_id = str(uuid4())
    return StreamingResponse(
        ai_service.stream(req.query, experience_id=experience_id),
        media_type="text/plain",
        headers={"X-Experience-ID": experience_id},
    )


@app.post("/models/warmup")
def warmup_model():
    try:
        ai_service.warmup()
        return {"status": "ready", "model": ai_service.model_name}
    except Exception as error:
        raise HTTPException(status_code=503, detail=str(error)) from error


@app.post("/internal/respond")
def internal_respond(req: InternalRespondRequest, x_internal_token: str | None = Header(default=None)):
    expected_token = os.getenv("AI_SERVICE_TOKEN", "")
    if expected_token and x_internal_token != expected_token:
        raise HTTPException(status_code=401, detail="invalid internal token")
    answer = character_service.respond(
        character_name=req.character_name, prompt_key=req.prompt_key, model_name=req.model_name,
        conversation_type=req.conversation_type, context=req.context, message=req.message,
    )
    return {"answer": answer[:500], "character_id": req.character_id,
            "conversation_id": req.conversation_id}


@app.post("/experiences/{experience_id}/review")
def review_experience(experience_id: str, req: ExperienceReviewRequest):
    try:
        return ai_service.experience_memory.review(experience_id, req.status, req.score, req.comment)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
