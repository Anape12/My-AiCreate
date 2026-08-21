from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path
from uuid import uuid4

from ai_service import AIService


class ChatRequest(BaseModel):
    query: str


class ExperienceReviewRequest(BaseModel):
    status: str
    score: int | None = None
    comment: str = ""


app = FastAPI()
ai_service = AIService()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory=Path(__file__).resolve().parent / "static"), name="static")


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


@app.post("/experiences/{experience_id}/review")
def review_experience(experience_id: str, req: ExperienceReviewRequest):
    try:
        return ai_service.experience_memory.review(experience_id, req.status, req.score, req.comment)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
