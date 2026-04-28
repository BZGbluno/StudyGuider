from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
import os
import asyncpg
from fastapi.responses import JSONResponse
from fastapi import status
import logging
import uuid
from api.auth import verify_jwt
import redis.asyncio as redis

logger = logging.getLogger(__name__)
router = APIRouter()

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    db=int(os.getenv("REDIS_DB", "0")),
    decode_responses=True,
)

# 24h: long enough for user to resume across normal idle gaps; refreshed on every openChapter.
ACTIVE_CHAPTER_TTL_SECONDS = 60 * 60 * 24


def _active_chapter_key(supabase_uid: str, textbook_id) -> str:
    return f"active_chapter:{supabase_uid}:{textbook_id}"

class ChapterRequest(BaseModel):
    textbook: int
    user_id: str

#Used to reopen a chapter with Redis cache
class ChapterOpenRequest(BaseModel):
    textbook: int
    chapter: str
    user_id: str


@router.get("/api/getChapters")
async def getChapters_endpoint(textbook_id: int, user_id = Depends(verify_jwt)):

    '''
    This api is used to retrieve every chapter within a textbook given
    a existing textbook title
    '''

    supabase_uid = user_id.get("sub")
    if not supabase_uid:
        raise HTTPException(status_code=401, detail="Missing UID")
    conn = None

    try:
        conn = await asyncpg.connect(
        host=os.getenv("DATABASE_HOST"),
        database=os.getenv("DATABASE_NAME"),
        user=os.getenv("DATABASE_USER"),
        password=os.getenv("DATABASE_PASSWORD")
        )

        rows = await conn.fetch(
            "SELECT chapter_number FROM chapters WHERE textbook_id = $1 ORDER BY chapter_number;",
            textbook_id
        )

        if not rows:
            raise HTTPException(status_code=404, detail="Chapter Titles not found")

        chapters = [row["chapter_number"] for row in rows]

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"response": chapters}
        )
    
    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    finally:
        if conn is not None:
            await conn.close()


@router.get("/api/redis/health")
async def redis_health():
    try:
        pong = await redis_client.ping()
        return {"ok": bool(pong)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis error: {str(e)}")


@router.get("/api/activeChapter")
async def get_active_chapter(textbook_id: int, user_id=Depends(verify_jwt)):
    """Return the last opened chapter for (user, textbook) or null if none cached."""
    supabase_uid = user_id.get("sub")
    if not supabase_uid:
        raise HTTPException(status_code=401, detail="Missing UID")

    key = _active_chapter_key(supabase_uid, textbook_id)
    try:
        raw = await redis_client.get(key)
    except Exception as e:
        logger.exception("activeChapter Redis error")
        raise HTTPException(status_code=500, detail=f"Redis error: {str(e)}")

    print(f"[activeChapter] key={key} value={raw!r}", flush=True)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"active_chapter": raw if raw else None},
    )


@router.post("/api/openChapter")
async def openChapter_endpoint(request: ChapterOpenRequest, user_id=Depends(verify_jwt)):
    supabase_uid = user_id.get("sub")
    if not supabase_uid:
        raise HTTPException(status_code=401, detail="Missing UID")

    # Always log once per request (Docker / uvicorn stdout). Browser DevTools will NOT show this.
    print(
        f"[openChapter] uid={supabase_uid} textbook={request.textbook} chapter={request.chapter!r}",
        flush=True,
    )
    logger.info(
        "openChapter textbook=%s chapter=%s uid=%s",
        request.textbook,
        request.chapter,
        supabase_uid,
    )

    chapter_label = request.chapter
    #detail_key = f"chapter:{request.textbook}:{chapter_label}:{supabase_uid}"
    active_key = _active_chapter_key(supabase_uid, request.textbook)

    try:
        # Refresh both: per-chapter detail key (existing behavior) and the canonical
        # "last opened chapter" key that powers GET /api/activeChapter.
        #await redis_client.set(detail_key, chapter_label, ex=ACTIVE_CHAPTER_TTL_SECONDS)
        await redis_client.set(active_key, chapter_label, ex=ACTIVE_CHAPTER_TTL_SECONDS)
        print(
            f"[Redis] SET active={active_key} value={chapter_label}",
            flush=True,
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "response": "Chapter opened successfully",
                "active_chapter": chapter_label,
            },
        )

    except Exception as e:
        logger.exception("openChapter Redis error")
        raise HTTPException(status_code=500, detail=f"Redis error: {str(e)}")

