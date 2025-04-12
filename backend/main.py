from fastapi import FastAPI
from api.generate import router as generate_router
from api.textbooks import router as textbooks_router
from api.chapter import router as chapter_router
from api.generateFlashCard import router as flashcard_router
from api.generateSummary import router as summary_router
app = FastAPI()

# Register endpoints
app.include_router(generate_router)
app.include_router(textbooks_router)
app.include_router(chapter_router)
app.include_router(flashcard_router)
app.include_router(summary_router)


# uvicorn main:app --reload
