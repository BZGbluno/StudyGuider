from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import os 
import asyncpg
from fastapi import status
from fastapi.responses import JSONResponse
import re

from .openAIHelper import get_openai_response

router = APIRouter()

class SummaryRequest(BaseModel):
    textbook: str
    chapter: str


@router.post("/api/generateSummary")
async def generate_endpoint(request: SummaryRequest):
    '''
    This endpoint returns a summary of an entire chapter using OPEN AI
    '''

    chapter = request.chapter
    textbook = request.textbook

    try:
        conn = await asyncpg.connect(
        host=os.getenv("DATABASE_HOST"),
        database=os.getenv("DATABASE_NAME"),
        user=os.getenv("DATABASE_USER"),
        password=os.getenv("DATABASE_PASSWORD")
        )
    

        # Gather chapter from textbook
        res = await conn.fetchrow("""
            SELECT c.textbook_id, c.chapter_number
            FROM chapters c
            JOIN textbooks t ON c.textbook_id = t.id
            WHERE t.title = $1 AND c.chapter_title = $2;
        """, textbook, chapter)

        if res == None:
            raise HTTPException(status_code=404, detail="Chapter not found in textbook.")

        # Extract the amount of chunks in the chapter
        textbook_id = res["textbook_id"]
        chapter_number = res["chapter_number"]

        all_chunk = await conn.fetch("""
        SELECT chunk_text 
        FROM chapter_embeddings 
        WHERE textbook_id = $1 AND chapter_number = $2;
        """, textbook_id, chapter_number)

        if all_chunk == None:
            raise HTTPException(status_code=404, detail="No chunks from in database")
        

        def clean_chunk(text):
            text = text.strip()
            text = re.sub(r"\n+", " ", text)
            return text

        # Flatten + clean all chunks into one big text blob
        chapter_text = " ".join(
            clean_chunk(row["chunk_text"])
            for row in all_chunk
            if row["chunk_text"].strip()
        )

        # Build the prompt for OpenAI
        prompt = f"""
        Summarize the following chapter so that a student can easily understand the main ideas, key concepts, and important details. Use clear and simple language.

        Chapter Content:
        {chapter_text}
        """

        try:
            modelResponse = await get_openai_response(prompt)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")


        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"response": modelResponse}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    finally:
        await conn.close()