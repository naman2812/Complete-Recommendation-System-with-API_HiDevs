from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    interests = Column(String)  # Stored as comma-separated values or JSON string
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    skills = relationship("UserSkill", back_populates="user")
    interactions = relationship("Interaction", back_populates="user")


class Content(Base):
    __tablename__ = "content"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    category = Column(String, index=True)
    difficulty = Column(String)  # e.g., 'Beginner', 'Intermediate', 'Advanced'
    popularity = Column(Float, default=0.0)

    skills = relationship("ContentSkill", back_populates="content")
    interactions = relationship("Interaction", back_populates="content")


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)


class UserSkill(Base):
    __tablename__ = "user_skills"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    skill_id = Column(Integer, ForeignKey("skills.id"), primary_key=True)
    proficiency = Column(Float, default=0.5)  # 0.0 to 1.0

    user = relationship("User", back_populates="skills")
    skill = relationship("Skill")


class ContentSkill(Base):
    __tablename__ = "content_skills"

    content_id = Column(Integer, ForeignKey("content.id"), primary_key=True)
    skill_id = Column(Integer, ForeignKey("skills.id"), primary_key=True)

    content = relationship("Content", back_populates="skills")
    skill = relationship("Skill")


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(
        Integer, primary_key=True, index=True
    )  # Adding surrogate key for ease of use
    user_id = Column(Integer, ForeignKey("users.id"))
    content_id = Column(Integer, ForeignKey("content.id"))
    type = Column(String)  # 'view', 'like', 'complete', 'rating'
    rating = Column(Float, nullable=True)  # e.g., 1-5
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="interactions")
    content = relationship("Content", back_populates="interactions")
