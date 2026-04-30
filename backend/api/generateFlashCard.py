from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from uuid import UUID
import os
import asyncpg
import random
import logging
import uuid

from .AIHelper import get_gemini_response
from api.auth import verify_jwt

router = APIRouter()
logger = logging.getLogger(__name__)


class FlashRequest(BaseModel):
    textbook_id: UUID
    chapter_number: int
    count: int


@router.post("/api/generateFlashCard")
async def generate_endpoint(request: FlashRequest, user_valid=Depends(verify_jwt)):
    """
    Generate `count` flashcards for the given chapter.

    Spaced-repetition strategy:
      1. Reuse this user's previously generated flashcards for the chapter that
         haven't been shown in over a day, oldest-seen first.
      2. If we still need more cards to reach `count`, generate fresh ones from
         random chunks via Gemini and persist them.
    """
    user_id = user_valid.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Missing UID")

    request_id = str(uuid.uuid4())
    textbook_id = request.textbook_id
    chapter_number = request.chapter_number
    count = request.count

    logger.info(
        f"[{request_id}] Flashcard request user={user_id} "
        f"textbook={textbook_id} chapter={chapter_number} count={count}"
    )

    if count <= 0:
        raise HTTPException(status_code=400, detail="count must be greater than zero")

    conn = None
    try:
        try:
            conn = await asyncpg.connect(
                host=os.getenv("DATABASE_HOST"),
                database=os.getenv("DATABASE_NAME"),
                user=os.getenv("DATABASE_USER"),
                password=os.getenv("DATABASE_PASSWORD"),
            )
        except Exception:
            logger.exception(f"[{request_id}] Failed to connect to database")
            raise HTTPException(status_code=500, detail="Failed to connect to database.")

        chapter_row = await conn.fetchrow(
            """
            SELECT 1
            FROM chapters
            WHERE textbook_id = $1 AND chapter_number = $2;
            """,
            textbook_id, chapter_number,
        )
        if chapter_row is None:
            raise HTTPException(status_code=400, detail="Invalid textbook or chapter")

        flashcards = []

        cached_rows = await conn.fetch(
            """
            SELECT fc_id, question, answer
            FROM master_flashcard
            WHERE textbook_id = $1
              AND chapter_number = $2
              AND user_id = $3
              AND last_seen < NOW() - INTERVAL '1 day'
            ORDER BY last_seen ASC
            LIMIT $4;
            """,
            textbook_id, chapter_number, user_id, count,
        )

        for row in cached_rows:
            flashcards.append({
                "id": row["fc_id"],
                "front": row["question"],
                "back": row["answer"],
            })

        if cached_rows:
            cached_ids = [row["fc_id"] for row in cached_rows]
            await conn.execute(
                "UPDATE master_flashcard SET last_seen = NOW() WHERE fc_id = ANY($1::int[]);",
                cached_ids,
            )
            logger.info(f"[{request_id}] Reused {len(cached_rows)} cached flashcards")

        remaining = count - len(flashcards)

        if remaining > 0:
            chunk_count_row = await conn.fetchrow(
                """
                SELECT COUNT(*)
                FROM chapter_embeddings
                WHERE textbook_id = $1 AND chapter_number = $2;
                """,
                textbook_id, chapter_number,
            )
            chunk_count = int(chunk_count_row["count"])

            if chunk_count <= 0:
                if not flashcards:
                    raise HTTPException(
                        status_code=404,
                        detail="No text chunks found for the given chapter.",
                    )
                logger.warning(
                    f"[{request_id}] No chunks available; returning "
                    f"{len(flashcards)} cached cards only"
                )
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"response": flashcards},
                )

            to_generate = min(remaining, chunk_count)
            selected_chunks = set()
            error_count = 0
            new_added = 0
            # Keep trying until we either fill the target or hit a reasonable
            # attempt budget (some chunks fail to parse cleanly; we don't want
            # one bad chunk to short the user a card).
            attempts_remaining = max(chunk_count * 2, to_generate * 3)

            logger.info(
                f"[{request_id}] Generating {to_generate} new flashcards "
                f"(chunks available: {chunk_count})"
            )

            while new_added < to_generate and attempts_remaining > 0:
                attempts_remaining -= 1

                if len(selected_chunks) < chunk_count:
                    while True:
                        random_chunk = random.randint(1, chunk_count)
                        if random_chunk not in selected_chunks:
                            selected_chunks.add(random_chunk)
                            break
                else:
                    # All distinct chunks have been tried; allow reuse so a
                    # parse-fail chunk doesn't bottleneck small chapters.
                    random_chunk = random.randint(1, chunk_count)

                chunk = await conn.fetchrow(
                    """
                    SELECT chunk_text
                    FROM chapter_embeddings
                    WHERE textbook_id = $1 AND chapter_number = $2 AND chunk_index = $3;
                    """,
                    textbook_id, chapter_number, random_chunk,
                )
                if chunk is None:
                    continue

                prompt = (
                    f"Context: {chunk['chunk_text']}\n"
                    "Create a question using the context and provide an answer to the question.\n"
                    "Format:\nQuestion:\nAnswer:"
                )

                try:
                    model_response = await get_gemini_response(prompt)
                except Exception:
                    error_count += 1
                    if error_count >= 6:
                        logger.error(
                            f"[{request_id}] Too many LLM failures ({error_count}), stopping early"
                        )
                        break
                    continue

                if "Answer:" not in model_response:
                    continue

                question, answer = model_response.split("Answer:", 1)
                question = question.replace("Question:", "").strip().rstrip("?")
                answer = answer.strip()
                if not question or not answer:
                    continue

                try:
                    fc_id = await conn.fetchval(
                        """
                        INSERT INTO master_flashcard
                            (textbook_id, chapter_number, question, answer, chunk_index, user_id)
                        VALUES ($1, $2, $3, $4, $5, $6)
                        RETURNING fc_id;
                        """,
                        textbook_id, chapter_number, question, answer, random_chunk, user_id,
                    )
                    await conn.execute(
                        """
                        INSERT INTO seen_card (user_id, flashcard_id)
                        VALUES ($1, $2)
                        ON CONFLICT DO NOTHING;
                        """,
                        user_id, fc_id,
                    )
                except Exception:
                    logger.exception(
                        f"[{request_id}] Failed to persist generated flashcard"
                    )
                    continue

                flashcards.append({"id": fc_id, "front": question, "back": answer})
                new_added += 1

        if not flashcards:
            logger.warning(f"[{request_id}] No valid flashcards generated")
            raise HTTPException(status_code=422, detail="No valid flashcards were generated.")

        logger.info(f"[{request_id}] Returning {len(flashcards)} flashcards")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"response": flashcards},
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"[{request_id}] Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if conn is not None:
            await conn.close()
