from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import asyncpg
import os

router = APIRouter()


@router.get("/api/getTextbooks")
async def getTextbooks_endpoint():
    try:
        conn = await asyncpg.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD")
        )

        rows = await conn.fetch("SELECT title FROM textbooks;")
        await conn.close()

        textbooks = [row["title"] for row in rows]

        return {"response": textbooks}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    





