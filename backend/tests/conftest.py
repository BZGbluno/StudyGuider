import pytest
import asyncpg
import os
import pytest_asyncio
from fastapi.testclient import TestClient
from main import app
import boto3
from moto import mock_aws
import api.s3
from api.s3 import delete_textbook_s3
from unittest.mock import patch

BUCKET = "test-textbooks"
USER_ID = "e6a6c7c5-4360-4722-8c0a-75ff8bff5b1f"

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
    
@pytest.fixture
def s3_bucket():
    with mock_aws():
        mock_s3 = boto3.client("s3", region_name="us-east-1")
        mock_s3.create_bucket(Bucket=BUCKET)

        with patch("api.s3.s3", mock_s3), patch("api.s3.BUCKET", BUCKET):
            yield mock_s3

def upload_fake_textbook(s3_client, user_id: str, textbook_id) -> None:
    keys = [
        f"users/{user_id}/textbooks/{textbook_id}/chapter1.pdf",
        f"users/{user_id}/textbooks/{textbook_id}/chapter2.pdf",
        f"users/{user_id}/textbooks/{textbook_id}/metadata.json",
    ]
    for key in keys:
        s3_client.put_object(Bucket=BUCKET, Key=key, Body=b"fake content")
