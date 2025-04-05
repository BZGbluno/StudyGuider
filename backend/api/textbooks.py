from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import psycopg2
import os

router = APIRouter()

@router.get("/api/getTextbooks")
def getTextbooks_endpoint():

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

    getAllTextBooksQuery = """
    SELECT
        name
    FROM textbooks;
    """

    cur.execute(getAllTextBooksQuery)
    res = cur.fetchall()

    print(res)

    textbooks = [row[0] for row in res]  # Extract names from tuples

    return {"response": textbooks}

    





