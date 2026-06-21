import sys
import os
import random
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import SessionLocal, Base, engine
from database.models import User, Content, Skill, UserSkill, ContentSkill, Interaction

def seed():
    # Recreate tables
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    
    # Create Skills
    skills = ["Python", "Data Science", "Machine Learning", "FastAPI", "SQL", "Deep Learning", "React", "Docker"]
    db_skills = []
    for s in skills:
        skill = Skill(name=s)
        db.add(skill)
        db_skills.append(skill)
    db.commit()

    # Create Users
    user_names = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Heidi", "Ivan", "Judy", "Karl", "Leo"]
    db_users = []
    for name in user_names:
        user = User(name=name, interests="coding,reading")
        db.add(user)
        db_users.append(user)
    db.commit()

    # Create Content
    content_data = [
        ("Intro to Python", "Programming", "Beginner", 80.0),
        ("Advanced Python", "Programming", "Advanced", 60.0),
        ("Data Science 101", "Data", "Beginner", 90.0),
        ("Machine Learning Basics", "AI", "Intermediate", 75.0),
        ("FastAPI for Web", "Web", "Intermediate", 65.0),
        ("SQL Masterclass", "Database", "Advanced", 70.0),
        ("Deep Learning with PyTorch", "AI", "Advanced", 55.0),
        ("React Fundamentals", "Web", "Beginner", 85.0),
        ("Docker for Developers", "DevOps", "Intermediate", 60.0),
        ("Python for Finance", "Data", "Intermediate", 40.0),
        ("AI Ethics", "AI", "Beginner", 30.0),
        ("Building REST APIs", "Web", "Intermediate", 68.0),
        ("Database Design", "Database", "Beginner", 72.0),
        ("NLP Fundamentals", "AI", "Intermediate", 50.0),
        ("Frontend Architectures", "Web", "Advanced", 45.0),
        ("Microservices with Docker", "DevOps", "Advanced", 55.0),
        ("Data Visualization", "Data", "Beginner", 82.0),
        ("Pandas Mastery", "Data", "Intermediate", 77.0),
        ("Graph Databases", "Database", "Advanced", 35.0),
        ("Kubernetes Intro", "DevOps", "Advanced", 48.0)
    ]
    
    db_content = []
    for c in content_data:
        content = Content(title=c[0], category=c[1], difficulty=c[2], popularity=c[3])
        db.add(content)
        db_content.append(content)
    db.commit()

    # Assign skills to content (randomly)
    for c in db_content:
        num_skills = random.randint(1, 3)
        assigned = random.sample(db_skills, num_skills)
        for s in assigned:
            db.add(ContentSkill(content_id=c.id, skill_id=s.id))
    db.commit()

    # Assign skills to users (randomly)
    for u in db_users:
        num_skills = random.randint(1, 4)
        assigned = random.sample(db_skills, num_skills)
        for s in assigned:
            db.add(UserSkill(user_id=u.id, skill_id=s.id, proficiency=random.random()))
    db.commit()

    # Create interactions
    types = ["view", "like", "complete", "rating"]
    for _ in range(100):
        u = random.choice(db_users)
        c = random.choice(db_content)
        t = random.choice(types)
        r = random.uniform(1, 5) if t == "rating" else None
        
        interaction = Interaction(user_id=u.id, content_id=c.id, type=t, rating=r)
        db.add(interaction)
    
    db.commit()
    print("Database seeded successfully with users, content, and interactions.")

if __name__ == "__main__":
    seed()
