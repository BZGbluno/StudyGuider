import os

# Make sure import-time env-var reads in `main` and its dependencies don't blow
# up under pytest when running outside docker / without a real .env file.
os.environ.setdefault("SUPABASE_URL", "http://localhost.invalid")
os.environ.setdefault("DATABASE_HOST", "localhost.invalid")
os.environ.setdefault("DATABASE_NAME", "fake")
os.environ.setdefault("DATABASE_USER", "fake")
os.environ.setdefault("DATABASE_PASSWORD", "fake")
os.environ.setdefault("OPENAI_API_KEY", "sk-fake")

import pytest
from fastapi.testclient import TestClient

from main import app
from api.auth import verify_jwt


FAKE_USER_ID = "00000000-0000-0000-0000-000000000001"


@pytest.fixture
def fake_user_id():
    return FAKE_USER_ID


@pytest.fixture
def client():
    """TestClient with verify_jwt overridden to a fixed authenticated user."""
    app.dependency_overrides[verify_jwt] = lambda: {"sub": FAKE_USER_ID}
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
