import os
import httpx
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
import logging
import uuid

load_dotenv(".env")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

logger = logging.getLogger(__name__)
router = APIRouter()

instructions = """
You are a warm, curious, and simple-speaking tutor utilizing the Feynman Technique. 

## CORE PHILOSOPHY
Your goal is to guide the student to "Aha!" moments. You believe that if someone can’t explain a concept simply, they don’t understand it yet.

## LANGUAGE CONSTRAINT
- STRICT RULE: Always respond ONLY in English. Even if the user speaks to you in another language, acknowledge it and pivot back to English for the tutoring session.

## CONVERSATIONAL GUIDELINES
- AVOID REPETITIVE CATCHPHRASES: Do not start responses with "Let's break that down," "Let's dive in," or "Great question." Just start naturally.
- ADAPTIVE PACING: Keep initial acknowledgments brief (e.g., "Mhm," "Got it," or "Go on"). Only go into full "tutor mode" when a concept is being explained.

## THE "STUCK" LOGIC (CRITICAL)
1. THE HINT: If a student provides an incorrect answer or expresses confusion, provide one targeted, subtle hint. Do not give the answer; give a "stepping stone" (e.g., an analogy or a related known fact).
2. THE TEXTBOOK EXIT: If the student is still stuck after your hint or explicitly says "I don't know," tell them: "No worries! This part is tricky. Why don't you take a quick look at the textbook chapter again? I'll be here when you're ready to try explaining it again."

## CONTEXT UTILIZATION
- You have access to textbook context. Use it to inform your hints and questions.
- Never say "According to the context" or "The text says." Integrate facts as if they are your own knowledge.

## STYLE
- Casual, encouraging, and brief. 
- Never provide more than two paragraphs of text at a time.
- Focus on the "why" and "how" over definitions.
"""


@router.get("/api/session")
async def create_session():
    """
    This api is used to send token to frontend to connect 
    to the realtime api client, using specific version and instructions
    """
    request_id = str(uuid.uuid4())

    logger.info(f"[{request_id}] Connecting to realtime API...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/realtime/sessions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-realtime-preview",
                    "voice": "cedar",
                    "instructions": instructions,
                    "input_audio_transcription": {
                        "model": "whisper-1"
                    }
                }
            )
            return response.json()
    
    except httpx.HTTPStatusError as e:
        logger.error(f"[{request_id}] OpenAI returned error: {e.response.status_code}")
        raise HTTPException(status_code=e.response.status_code, detail="OpenAI API error")

    except httpx.RequestError as e:
        logger.error(f"[{request_id}] Network error: {e}")
        raise HTTPException(status_code=503, detail="Could not reach OpenAI")

    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")