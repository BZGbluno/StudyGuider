from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from .embedding_utils import generate_Helper


router = APIRouter()

class PromptRequest(BaseModel):
    prompt: str
    textbook: str
    chapter: str


@router.post("/api/generate")
async def generate_endpoint(request: PromptRequest):


    prompt = request.prompt
    chapter = request.chapter
    textbook = request.textbook

    try:
        answer = await generate_Helper(prompt, chapter, textbook)
        return {"response": answer}
    
    except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))