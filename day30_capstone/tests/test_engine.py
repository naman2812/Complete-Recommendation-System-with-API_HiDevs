import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.database import Base
from database.repositories import UserRepository, ContentRepository, InteractionRepository
from engine.orchestrator import RecommendationOrchestrator

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_db_engine.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    u_repo = UserRepository(db)
    c_repo = ContentRepository(db)
    i_repo = InteractionRepository(db)
    
    u = u_repo.create_user("Alice")
    c1 = c_repo.create_content("Content 1", "Cat A", "Beg")
    c2 = c_repo.create_content("Content 2", "Cat A", "Adv")
    
    i_repo.record_interaction(u.id, c1.id, "view")
    
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

def test_get_recommendations(db):
    orchestrator = RecommendationOrchestrator(db)
    recs = orchestrator.get_recommendations(1, limit=5, strategy="hybrid")
    
    assert isinstance(recs, list)
    if len(recs) > 0:
        assert "breakdown" in recs[0]
        assert "popularity" in recs[0]["breakdown"]
    
    # Check cache works
    recs_cached = orchestrator.get_recommendations(1, limit=5, strategy="hybrid")
    assert recs == recs_cached

def test_cold_start(db):
    u_repo = UserRepository(db)
    u_repo.create_user("Bob") # user id 2
    
    orchestrator = RecommendationOrchestrator(db)
    recs = orchestrator.get_recommendations(2, limit=5)
    
    assert isinstance(recs, list)
    if len(recs) > 0:
        assert recs[0]["strategy"] == "cold_start_popular"
