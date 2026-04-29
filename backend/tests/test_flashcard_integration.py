import pytest
from fastapi.testclient import TestClient

def test_generate_flashcards_success(client):
    """
    tses generating flascards
    """
    response = client.post("/api/generateFlashCard", json={
        "textbook": "thinkpython2",
        "chapter": "Files",
        "count": 2
    })
    assert response.status_code == 200

    output_res = response.json()
    assert "response" in output_res, "Key 'response' missing in JSON"
    assert isinstance(output_res["response"], dict), "Response should be a dictionary of flashcards"
    assert len(output_res["response"]) <= 2, "returned more flashcards than requested"
    assert len(output_res["response"]) > 0, "no flashcards were returned"
    
    for key, value in output_res["response"].items():
        assert key.startswith("Question"), f"Unexpected key format: {key}"
        assert len(value) == 2, f"Flashcard should have question and answer pair, got: {value}"
    


