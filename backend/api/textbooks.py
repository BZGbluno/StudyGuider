from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import asyncpg
import os
from fastapi import status
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/api/getTextbooks")
async def getTextbooks_endpoint():
    '''
    This will extract every textbooks title, author, description,
    and image path
    '''
    try:
        conn = await asyncpg.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD")
        )

        rows = await conn.fetch("SELECT * FROM textbooks;")

        if rows == None:
            raise HTTPException(status_code=404, detail="Titles from textbooks not found")

        textbooks = [
            {
                "title": row["title"],
                "author": row["author"],
                "description": row["description"],
                "image_path": row["image_path"]
            }
            for row in rows
        ]

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"response": textbooks}
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        await conn.close()

    





