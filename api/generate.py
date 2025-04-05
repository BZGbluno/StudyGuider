from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from .embedding_utils import generate_Helper



router = APIRouter()

class PromptRequest(BaseModel):
    prompt: str
    textbook: str
    chapter: str


@router.get("/api/generate")
def generate_endpoint(request: PromptRequest):


    prompt = request.prompt
    chapter = request.chapter
    textbook = request.textbook

    answer = generate_Helper(prompt, chapter, textbook)
    return {"response": answer}
    




