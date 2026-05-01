from fastapi import APIRouter, HTTPException, Depends
import asyncpg
import os
import logging
import uuid
from api.auth import verify_jwt
import logging
router = APIRouter()
logger = logging.getLogger(__name__)
from uuid import UUID

@router.get("/api/getTextbooks")
async def getTextbooks_endpoint(user_id = Depends(verify_jwt)):
    request_id = str(uuid.uuid4())
    supabase_uid = user_id.get("sub")
    
    request_id = str(uuid.uuid4())
    if not supabase_uid:
        raise HTTPException(status_code=401, detail="Missing UID")
    conn = None
    try:
        logger.info(f"[{request_id}] Connecting to database")

        conn = await asyncpg.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD")
        )

        rows = await conn.fetch(
            "SELECT id, title, status FROM textbooks WHERE user_uid = $1 AND status = 'complete';",
            supabase_uid,
        )

        return [
            {
                "id": row["id"],
                "title": row["title"],
                "status": row["status"],
            }
            for row in rows
        ]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Database error", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if conn is not None:
            await conn.close()
'''
getTextbooks_endpoint:
Fetches the authenticated user's completed textbooks and returns a list of
dictionaries containing id, title, and status.

Connects asynchronously to PostgreSQL using environment variables, filters
the 'textbooks' table by user_uid and status = 'complete', and returns the
rows in a JSON-friendly format (empty list if none).

Raises HTTPException(401) if the JWT is missing a UID, or HTTPException(500)
for any database errors.
'''
    
    
@router.get("/api/getTextbookTitle")
async def get_textbook_title(
    textbook_id: UUID,
    user_valid=Depends(verify_jwt)
):
    conn = None
    try:
        supabase_uid = user_valid.get("sub")
        if not supabase_uid:
            raise HTTPException(status_code=401, detail="Missing UID")

        conn = await asyncpg.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
        )

        row = await conn.fetchrow(
            """
            SELECT title
            FROM textbooks
            WHERE id = $1 AND user_uid = $2
            """,
            textbook_id,
            supabase_uid,
        )

        if not row:
            raise HTTPException(status_code=404, detail="Textbook not found")

        return {
            "title": row["title"]
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    finally:
        if conn:
            await conn.close()


@router.get("/api/getMetadata/{bookID}/{chapterID}")
async def get_mastery_metadata(
    bookID: UUID,
    chapterID: int,
    user_valid=Depends(verify_jwt)
):
    conn = None
    try:
        supabase_uid = user_valid.get("sub")
        if not supabase_uid:
            raise HTTPException(status_code=401, detail="Missing UID")
        
        conn = await asyncpg.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
        )

        row = await conn.fetchrow(
            """
            SELECT t.title as book_title, c.chapter_title 
            FROM textbooks t
            JOIN chapters c ON c.textbook_id = t.id
            WHERE t.id = $1 AND c.chapter_number = $2 AND t.user_uid = $3
            """,
            bookID,
            chapterID,
            supabase_uid,
        )

        if not row:
            raise HTTPException(status_code=404, detail="Textbook not found")
        
        return {
            "textbookTitle": row["book_title"],
            "chapterTitle": row["chapter_title"]
        }
    
    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    finally:
        if conn:
            await conn.close()
        



