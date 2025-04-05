from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import psycopg2
import os

router = APIRouter()

class ChapterRequest(BaseModel):
    textbook: str


@router.get("/api/getChapters")
def getChapters_endpoint(request:ChapterRequest):

    textbookName = request.textbook

    # conn = psycopg2.connect(
    #     host="localhost",
    #     database="mydb",
    #     user="bruno",
    #     password="your_password"
    # )
    conn = psycopg2.connect(
    host=os.getenv("DATABASE_HOST"),
    database=os.getenv("DATABASE_NAME"),
    user=os.getenv("DATABASE_USER"),
    password=os.getenv("DATABASE_PASSWORD")
    )
    cur = conn.cursor()

    findTextBookIDQuery = """
    SELECT
        id
    FROM textbooks
    WHERE name = %s;
    """

    cur.execute(findTextBookIDQuery, (textbookName,))
    res = cur.fetchone()

    textBookId = res[0]

    findAllChapters = """
    SELECT
        chapter_title
    FROM chapters
    WHERE textbook_id = %s;
    """
    cur.execute(findAllChapters, (textBookId,))
    allTextBooksChapters = cur.fetchall()

    chapters = [row[0] for row in allTextBooksChapters]

    return {"response": chapters}