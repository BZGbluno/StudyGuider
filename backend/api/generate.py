from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from .embedding_utils import generate_Helper
from fastapi import status
from fastapi.responses import JSONResponse


router = APIRouter()

class PromptRequest(BaseModel):
    prompt: str
    textbook: str
    chapter: str


@router.post("/api/generate")
async def generate_endpoint(request: PromptRequest):
    '''
    This will generate a response using a prompt and provide 
    context to the prompt using a corresponding textbook and
    chapter title
    '''

    prompt = request.prompt
    chapter = request.chapter
    textbook = request.textbook

    try:
        modelResponse = await generate_Helper(prompt, chapter, textbook)

        if modelResponse is None:

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred on the server."
            )

        return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"response": modelResponse}
        )
    
    except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))