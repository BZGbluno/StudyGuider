from fastapi import FastAPI
from api.generate import router as generate_router
from api.textbooks import router as textbooks_router
from api.chapter import router as chapter_router
app = FastAPI()

# Register route
app.include_router(generate_router)
app.include_router(textbooks_router)
app.include_router(chapter_router)

# Optional root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to StudyGuider API!"}



# uvicorn main:app --reload
