import pytest
import asyncpg
import os
import pytest_asyncio
from fastapi.testclient import TestClient
from main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest_asyncio.fixture
async def db():
    conn = await asyncpg.connect(
        host=os.getenv("DATABASE_HOST"),
        database=os.getenv("DATABASE_NAME"),
        user=os.getenv("DATABASE_USER"),
        password=os.getenv("DATABASE_PASSWORD")
    )
    yield conn
    await conn.close()

@pytest_asyncio.fixture
async def textbook(db, test_user):  
    row = await db.fetchrow(
        "INSERT INTO textbooks (title, user_uid, author, description, image_path, status) VALUES ($1, $2, $3, $4, $5, $6) RETURNING id",
        'Test Book', 'e6a6c7c5-4360-4722-8c0a-75ff8bff5b1f', 'Test Author', 'Test description', '/test.jpg', 'active'
    )
    yield row['id']
    

@pytest_asyncio.fixture
async def test_user(db):  
    await db.execute(  
        "INSERT INTO users (supabase_uid) VALUES ($1) ON CONFLICT DO NOTHING",
        'e6a6c7c5-4360-4722-8c0a-75ff8bff5b1f'
    )
    yield 'e6a6c7c5-4360-4722-8c0a-75ff8bff5b1f'
    