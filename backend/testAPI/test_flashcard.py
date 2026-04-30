"""
Unit tests for POST /api/generateFlashCard.

Mocks asyncpg and the Gemini call so tests run hermetically (no real DB / no
network). Auth is bypassed via the `client` fixture in conftest.py.
"""
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest


TEXTBOOK_ID = str(uuid4())


class FakeConn:
    """Minimal stand-in for an asyncpg connection covering the calls the
    flashcard endpoint makes."""

    def __init__(self, *, chapter_exists=True, cached=None, chunk_count=10):
        self.chapter_exists = chapter_exists
        self.cached = list(cached or [])
        self.chunk_count = chunk_count
        self._fc_id = 100
        self.executed = []  # (query, args) for assertions if needed

    async def fetchrow(self, query, *args):
        q = " ".join(query.split())
        if "FROM chapters" in q:
            return {"ok": 1} if self.chapter_exists else None
        if "COUNT(*)" in q and "chapter_embeddings" in q:
            return {"count": self.chunk_count}
        if "chunk_text" in q and "chapter_embeddings" in q:
            return {"chunk_text": f"chunk text for index {args[2]}"}
        return None

    async def fetch(self, query, *args):
        q = " ".join(query.split())
        if "FROM master_flashcard" in q:
            limit = args[3] if len(args) >= 4 else len(self.cached)
            return self.cached[:limit]
        return []

    async def fetchval(self, query, *args):
        self._fc_id += 1
        return self._fc_id

    async def execute(self, query, *args):
        self.executed.append((query, args))

    async def close(self):
        pass


def _patch_db_and_llm(fake_conn, gemini_mock):
    """Context manager helper that patches asyncpg.connect and Gemini."""
    return (
        patch(
            "api.generateFlashCard.asyncpg.connect",
            new=AsyncMock(return_value=fake_conn),
        ),
        patch(
            "api.generateFlashCard.get_gemini_response",
            new=gemini_mock,
        ),
    )


def _body(count=3):
    return {"textbook_id": TEXTBOOK_ID, "chapter_number": 1, "count": count}


def test_count_zero_returns_400(client):
    response = client.post("/api/generateFlashCard", json=_body(count=0))
    assert response.status_code == 400


def test_invalid_chapter_returns_400(client):
    fake_conn = FakeConn(chapter_exists=False)
    gemini = AsyncMock(return_value="Question: x\nAnswer: y")
    p1, p2 = _patch_db_and_llm(fake_conn, gemini)
    with p1, p2:
        response = client.post("/api/generateFlashCard", json=_body())
    assert response.status_code == 400
    gemini.assert_not_called()


def test_no_chunks_and_no_cache_returns_404(client):
    fake_conn = FakeConn(chunk_count=0, cached=[])
    gemini = AsyncMock(return_value="Question: x\nAnswer: y")
    p1, p2 = _patch_db_and_llm(fake_conn, gemini)
    with p1, p2:
        response = client.post("/api/generateFlashCard", json=_body())
    assert response.status_code == 404
    gemini.assert_not_called()


def test_returns_cached_flashcards_without_calling_llm(client):
    cached = [
        {"fc_id": 11, "question": "Q1", "answer": "A1"},
        {"fc_id": 12, "question": "Q2", "answer": "A2"},
        {"fc_id": 13, "question": "Q3", "answer": "A3"},
    ]
    fake_conn = FakeConn(cached=cached)
    gemini = AsyncMock(return_value="Question: x\nAnswer: y")
    p1, p2 = _patch_db_and_llm(fake_conn, gemini)
    with p1, p2:
        response = client.post("/api/generateFlashCard", json=_body(count=3))

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body["response"], list)
    assert len(body["response"]) == 3
    assert body["response"][0] == {"id": 11, "front": "Q1", "back": "A1"}
    gemini.assert_not_called()


def test_generates_when_cache_empty(client):
    fake_conn = FakeConn(cached=[], chunk_count=10)
    gemini = AsyncMock(return_value="Question: What is X?\nAnswer: It is Y.")
    p1, p2 = _patch_db_and_llm(fake_conn, gemini)
    with p1, p2:
        response = client.post("/api/generateFlashCard", json=_body(count=3))

    assert response.status_code == 200
    body = response.json()
    assert len(body["response"]) == 3
    for card in body["response"]:
        assert set(card.keys()) == {"id", "front", "back"}
    # Trailing '?' is stripped from the question; answer is preserved.
    assert body["response"][0]["front"] == "What is X"
    assert body["response"][0]["back"] == "It is Y."
    assert gemini.await_count == 3


def test_mixes_cached_and_generated(client):
    cached = [
        {"fc_id": 11, "question": "Cached Q1", "answer": "Cached A1"},
        {"fc_id": 12, "question": "Cached Q2", "answer": "Cached A2"},
    ]
    fake_conn = FakeConn(cached=cached, chunk_count=10)
    gemini = AsyncMock(return_value="Question: New Q\nAnswer: New A")
    p1, p2 = _patch_db_and_llm(fake_conn, gemini)
    with p1, p2:
        response = client.post("/api/generateFlashCard", json=_body(count=5))

    assert response.status_code == 200
    body = response.json()
    assert len(body["response"]) == 5
    # Cached cards come first, in the order returned by the cache query.
    assert body["response"][0]["front"] == "Cached Q1"
    assert body["response"][1]["front"] == "Cached Q2"
    # Then newly generated ones.
    assert body["response"][2]["front"] == "New Q"
    # 5 total - 2 cached = 3 Gemini calls.
    assert gemini.await_count == 3


def test_caps_generation_at_chunk_count(client):
    """If `count` exceeds the number of chunks and there's no cache, we
    return at most `chunk_count` cards."""
    fake_conn = FakeConn(cached=[], chunk_count=2)
    gemini = AsyncMock(return_value="Question: Q\nAnswer: A")
    p1, p2 = _patch_db_and_llm(fake_conn, gemini)
    with p1, p2:
        response = client.post("/api/generateFlashCard", json=_body(count=10))

    assert response.status_code == 200
    body = response.json()
    assert len(body["response"]) == 2
    assert gemini.await_count == 2


def test_unauthenticated_request_returns_401(client):
    """No JWT override here -> verify_jwt should reject the call."""
    # Drop the override that the `client` fixture installed.
    from api.auth import verify_jwt
    from main import app

    app.dependency_overrides.pop(verify_jwt, None)

    response = client.post("/api/generateFlashCard", json=_body())
    assert response.status_code in (401, 403)
