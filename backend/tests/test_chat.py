import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

class MockProvider:
    async def __call__(self, prompt):
        return "mocked reply"

@pytest.fixture(autouse=True)
def patch_providers(monkeypatch):
    monkeypatch.setattr("app.providers.call_openai", MockProvider())
    monkeypatch.setattr("app.providers.call_gemini", MockProvider())
    monkeypatch.setattr("app.providers.stream_openai", lambda prompt: iter(["mocked stream"]))
    monkeypatch.setattr("app.providers.stream_gemini", lambda prompt: iter(["mocked stream"]))

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_chat():
    r = client.post("/api/chat", json={"message": "hello"})
    assert r.status_code == 200
    data = r.json()
    assert "reply" in data
    assert "providers" in data

def test_stream_chat():
    r = client.get("/api/chat/stream?message=hello")
    assert r.status_code == 200
    chunks = r.content.split(b"\n")
    assert any(b"event: chunk" in c for c in chunks)
    assert any(b"event: done" in c for c in chunks)
