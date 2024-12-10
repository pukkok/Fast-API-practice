import httpx
import pytest

BASE_URL = "http://127.0.0.1:8080"

@pytest.fixture(scope="module")
def client():
    with httpx.Client(base_url=BASE_URL) as client:
        yield client

def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "서버 접속 성공"}
