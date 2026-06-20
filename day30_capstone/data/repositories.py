from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any, Optional
from . import models

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user(self, user_id: int) -> Optional[models.User]:
        return self.db.query(models.User).filter(models.User.id == user_id).first()

    def get_all_users(self) -> List[models.User]:
        return self.db.query(models.User).all()
    
    def get_user_history(self, user_id: int) -> List[models.Interaction]:
        return self.db.query(models.Interaction).filter(models.Interaction.user_id == user_id).all()

    def create_user(self, name: str, interests: str = "") -> models.User:
        db_user = models.User(name=name, interests=interests)
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

class ContentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_content(self, content_id: int) -> Optional[models.Content]:
        return self.db.query(models.Content).filter(models.Content.id == content_id).first()

    def get_all_content(self) -> List[models.Content]:
        return self.db.query(models.Content).all()

    def get_content_by_skills(self, skill_ids: List[int]) -> List[models.Content]:
        # Returns content that has AT LEAST ONE of the required skills
        return self.db.query(models.Content).join(models.ContentSkill).filter(
            models.ContentSkill.skill_id.in_(skill_ids)
        ).all()

    def create_content(self, title: str, category: str, difficulty: str, popularity: float = 0.0) -> models.Content:
        db_content = models.Content(
            title=title, category=category, difficulty=difficulty, popularity=popularity
        )
        self.db.add(db_content)
        self.db.commit()
        self.db.refresh(db_content)
        return db_content

class InteractionRepository:
    def __init__(self, db: Session):
        self.db = db
        
    TYPE_WEIGHTS = {"view": 0.3, "like": 0.7, "complete": 1.0, "skip": -0.2, "rate": 0.0}

    def record_interaction(self, user_id: int, content_id: int, interaction_type: str, rating: Optional[float] = None) -> models.Interaction:
        db_interaction = models.Interaction(
            user_id=user_id, content_id=content_id, type=interaction_type, rating=rating
        )
        self.db.add(db_interaction)
        
        # Calculate implicit score
        if interaction_type == "rate" and rating is not None:
            score = rating / 5.0 # normalize 1-5 to 0-1
        else:
            score = self.TYPE_WEIGHTS.get(interaction_type, 0.0)
            
        # Update popularity based on the interaction score
        if score > 0:
            content = self.db.query(models.Content).filter(models.Content.id == content_id).first()
            if content:
                # Basic bump: add score. In a real system we'd normalize across total system interactions.
                content.popularity = min(content.popularity + score, 100.0)
                
        self.db.commit()
        self.db.refresh(db_interaction)
        return db_interaction

    def get_all_interactions(self) -> List[models.Interaction]:
        return self.db.query(models.Interaction).all()

class SkillRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_skill(self, name: str) -> models.Skill:
        db_skill = models.Skill(name=name)
        self.db.add(db_skill)
        self.db.commit()
        self.db.refresh(db_skill)
        return db_skill

    def assign_skill_to_user(self, user_id: int, skill_id: int, proficiency: float):
        db_user_skill = models.UserSkill(user_id=user_id, skill_id=skill_id, proficiency=proficiency)
        self.db.merge(db_user_skill) # merge handles insert or update
        self.db.commit()

    def assign_skill_to_content(self, content_id: int, skill_id: int):
        db_content_skill = models.ContentSkill(content_id=content_id, skill_id=skill_id)
        self.db.merge(db_content_skill)
        self.db.commit()
