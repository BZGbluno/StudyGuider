from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import psycopg2


router = APIRouter()

@router.get("/api/getTextbooks")
def getTextbooks_endpoint():

    conn = psycopg2.connect(
        host="localhost",
        database="mydb",
        user="bruno",
        password="your_password"
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

    





