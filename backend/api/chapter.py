from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import os
import asyncpg
from fastapi.responses import JSONResponse
from fastapi import status

router = APIRouter()


class ChapterRequest(BaseModel):
    textbook: str


@router.get("/api/getChapters")
async def getChapters_endpoint(textbook: str):
    '''
    This api is used to retrieve every chapter within a textbook given
    a existing textbook title
    '''

    try:
        conn = await asyncpg.connect(
        host=os.getenv("DATABASE_HOST"),
        database=os.getenv("DATABASE_NAME"),
        user=os.getenv("DATABASE_USER"),
        password=os.getenv("DATABASE_PASSWORD")
        )


        textbook_id = await conn.fetchval(
        "SELECT id FROM textbooks WHERE title = $1;",
        textbook)

        if textbook_id is None:
            raise HTTPException(status_code=404, detail="Textbook not found")


        rows = await conn.fetch(
            "SELECT chapter_title FROM chapters WHERE textbook_id = $1;",
            textbook_id
        )


        # select only chapter_titles from row
        chapters = [row["chapter_title"] for row in rows]

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"response": chapters}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    finally:
        await conn.close()