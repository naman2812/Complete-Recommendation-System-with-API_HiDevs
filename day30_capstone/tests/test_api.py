from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.app import app
from data.database import Base, get_db
from data.repositories import UserRepository, ContentRepository

# Test DB Setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_db_api.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

HEADERS = {"X-API-Key": "capstone-auth-key-2026"}

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    u_repo = UserRepository(db)
    u_repo.create_user("Test API User")
    
    c_repo = ContentRepository(db)
    c_repo.create_content("API Test Content", "Testing", "Beg")
    
    yield
    Base.metadata.drop_all(bind=engine)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200

def test_get_recommendations_no_auth():
    response = client.get("/recommend/1")
    assert response.status_code == 401

def test_get_recommendations():
    # User 1 should exist from setup
    response = client.get("/recommend/1?strategy=hybrid", headers=HEADERS)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    if len(response.json()) > 0:
        assert "breakdown" in response.json()[0]

def test_get_recommendations_not_found():
    response = client.get("/recommend/999", headers=HEADERS)
    assert response.status_code == 404

def test_record_feedback():
    response = client.post("/feedback", json={
        "user_id": 1,
        "content_id": 1,
        "interaction_type": "like",
        "rating": 5.0
    }, headers=HEADERS)
    assert response.status_code == 200

def test_get_metrics():
    response = client.get("/metrics", headers=HEADERS)
    assert response.status_code == 200
    assert "total_requests" in response.json()
