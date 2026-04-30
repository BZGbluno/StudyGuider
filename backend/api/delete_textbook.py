from fastapi import APIRouter, HTTPException, Depends
from fastapi import Response
import asyncpg
import os
import logging
from uuid import UUID
import uuid
from api.auth import verify_jwt
from api.s3 import delete_textbook_s3

logger = logging.getLogger(__name__)
router = APIRouter()


@router.delete("/api/delete_textbook")
async def delete_textbook(textbook_id: UUID, user_id = Depends(verify_jwt)):
    request_id = str(uuid.uuid4())
    '''
    This will delete given textbook id associated with given user id
    '''
    supabase_uid = user_id.get("sub")

    logger.info(f"[{request_id}] Deleting textbook {textbook_id} from user {supabase_uid}")


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

        result = await conn.execute(
            "DELETE FROM textbooks WHERE id = $1 AND user_uid = $2",
            textbook_id, supabase_uid
        )

        if result == "DELETE 0":
            raise HTTPException(status_code=404, detail="Textbook not found")

    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"[{request_id}] Database error", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    finally:
        if conn:
            await conn.close()

    #now delete from s3
    try:
        delete_textbook_s3(supabase_uid, textbook_id)
        logger.info(f"[{request_id}] Deleting from S3...")
    except Exception as e:
        logger.error(f"[{request_id}] S3 delete operation failed: {e}", exc_info=True)
    
    return Response(status_code=204)