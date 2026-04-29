import pytest
from fastapi.testclient import TestClient
from main import app
from api.auth import verify_jwt
import json
from conftest import upload_fake_textbook, USER_ID, BUCKET

def override_verify_jwt():
    return {"sub": "e6a6c7c5-4360-4722-8c0a-75ff8bff5b1f"}

app.dependency_overrides[verify_jwt] = override_verify_jwt

@pytest.mark.asyncio
async def test_delete_textbook_endpoint(client, db, textbook, s3_bucket): 
    """
    Test deleting textbook associated with certain user
    """
    upload_fake_textbook(s3_bucket, USER_ID, textbook)

    before = s3_bucket.list_objects_v2(
        Bucket=BUCKET,
        Prefix=f"users/{USER_ID}/textbooks/{textbook}/"
    )
    assert "Contents" in before
    
    # now delete via endpoint
    response = client.delete(f"/api/delete_textbook?textbook_id={str(textbook)}") 

    assert response.status_code == 204

    # query to check textbook DNE
    deleted = await db.fetchrow(
        "SELECT * FROM textbooks WHERE id = $1 AND user_uid = $2",
        textbook,
        "e6a6c7c5-4360-4722-8c0a-75ff8bff5b1f",  
    )
    assert deleted is None  

    after = s3_bucket.list_objects_v2(
        Bucket=BUCKET,
        Prefix=f"users/{USER_ID}/textbooks/{textbook}/"
    )
    assert after.get("Contents") is None