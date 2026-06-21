import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.database import Base
from database.models import User, Content, Skill
from database.repositories import UserRepository, ContentRepository, SkillRepository

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_db.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

def test_create_user(db):
    user_repo = UserRepository(db)
    user = user_repo.create_user(name="Test User", interests="testing")
    assert user.id is not None
    assert user.name == "Test User"
    
def test_create_content(db):
    content_repo = ContentRepository(db)
    content = content_repo.create_content(title="Test Content", category="Testing", difficulty="Beginner")
    assert content.id is not None
    assert content.title == "Test Content"

def test_create_skill(db):
    skill_repo = SkillRepository(db)
    skill = skill_repo.create_skill(name="Python")
    assert skill.id is not None
    assert skill.name == "Python"
