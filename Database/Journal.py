# Database/Journal.py
# Database models and connections for Eco-Journal

import importlib
import os
from datetime import datetime, date
from typing import Optional, List, Dict, Any
import uuid
from Database.db import Base, engine  # Import shared Base & engine

# PostgreSQL imports
from sqlalchemy import create_engine, Column, String, Integer, Float, Boolean, DateTime, Date, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

# MongoDB imports
from pymongo import MongoClient
from bson import ObjectId

# Environment variables
from dotenv import load_dotenv

load_dotenv()

# PostgreSQL Configuration
#POSTGRES_URL = os.getenv("POSTGRES_URL") #make changes after installation
#engine = create_engine(POSTGRES_URL)
#SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#Base = declarative_base()

# MongoDB Configuration
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/")
mongo_client = MongoClient(MONGO_URL)
mongo_db = mongo_client.ecoapp
journal_collection = mongo_db.journal_entries

class UserStats(Base):
    """PostgreSQL UserStats model for streak tracking"""
    __tablename__ = "user_stats"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False) 
    username = Column(String(50), unique=True, nullable=False)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    total_entries = Column(Integer, default=0)
    last_entry_date = Column(Date, nullable=True)
    streak_frozen = Column(Boolean, default=False)
    freeze_count = Column(Integer, default=0)
    max_freezes_per_month = Column(Integer, default=3)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class StreakEvent(Base):
    """PostgreSQL model for tracking streak events"""
    __tablename__ = "streak_events"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    event_type = Column(String(50), nullable=False)  # 'continued', 'broken', 'frozen', 'milestone'
    streak_count = Column(Integer, nullable=False)
    previous_streak = Column(Integer, default=0)
    # metadata = Column(JSON, nullable=True)  # Additional event data
    meta_info = Column("metadata", JSON, nullable=True)  # ✅ safe name in Python, DB column still "metadata"
    created_at = Column(DateTime, default=datetime.utcnow)

class Achievement(Base):
    """PostgreSQL model for user achievements"""
    __tablename__ = "achievements"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)# foreign key link to Auth.User.id
    achievement_type = Column(String(50), nullable=False)
    achievement_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    badge_emoji = Column(String(10), nullable=True)
    earned_at = Column(DateTime, default=datetime.utcnow)
    streak_count_when_earned = Column(Integer, nullable=True)


class DatabaseManager:
    """Manages both PostgreSQL and MongoDB connections"""
    
    def __init__(self):
        self.postgres_session = None
        self.mongo_collection = journal_collection
        self.setup_postgres()
        self.setup_mongodb()

    
    
    def setup_postgres(self):
        """Initialize PostgreSQL connection and create tables"""
        try:

            
            # Dynamically import other modules that define models so SQLAlchemy knows them.
        # Use full package path that matches your project (adjust if needed).
            try:
                importlib.import_module("backend.Auth.models")
                print("✅ Imported backend.Auth.models")
            except Exception as e:
            # show a helpful message but continue — if import fails, create_all won't include those models
                print(f"⚠️ Could not import backend.Auth.models: {e}")
            
            from Database.db import Base, engine, SessionLocal
            Base.metadata.create_all(bind=engine)
            self.postgres_session = SessionLocal()
            print("✅ PostgreSQL connection established")
        except Exception as e:
            print(f"❌ PostgreSQL connection failed: {e}")
            raise
    
    def setup_mongodb(self):
        """Initialize MongoDB connection and create indexes"""
        try:
            # Test connection
            mongo_client.admin.command('ping')
            
            # Create indexes for better performance
            self.mongo_collection.create_index("user_id")
            self.mongo_collection.create_index("created_at")
            self.mongo_collection.create_index("sentiment.label")
            
            print("✅ MongoDB connection established")
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            raise
    
    def get_postgres_session(self) -> Session:
        """Get PostgreSQL session"""
        if not self.postgres_session:
            self.postgres_session = SessionLocal()
        return self.postgres_session
    
    def close_connections(self):
        """Close all database connections"""
        if self.postgres_session:
            self.postgres_session.close()
        mongo_client.close()

class UserRepository:
    """Repository for UserStats operations"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def get_user_by_id(self, user_id: str) -> Optional[UserStats]:
        """Get user by ID"""
        return self.db.query(UserStats).filter(UserStats.user_id == user_id).first()
    
    def create_user(self, user_id: str, username: str = None) -> UserStats:
        """Create new user"""
        if not username:
            username = f"user_{user_id}"
        
        user = UserStats(
            user_id=user_id,
            username=username
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def update_user_streak(self, user_id: str, new_streak: int, entry_date: date) -> UserStats:
        """Update user streak information"""
        user = self.get_user_by_id(user_id)
        if not user:
            user = self.create_user(user_id)
        
        user.current_streak = new_streak
        user.total_entries += 1
        user.last_entry_date = entry_date
        user.updated_at = datetime.utcnow()
        
        if new_streak > user.longest_streak:
            user.longest_streak = new_streak
        
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def use_streak_freeze(self, user_id: str) -> bool:
        """Use a streak freeze for user"""
        user = self.get_user_by_id(user_id)
        if not user or user.freeze_count >= user.max_freezes_per_month:
            return False
        
        user.streak_frozen = True
        user.freeze_count += 1
        user.updated_at = datetime.utcnow()
        
        self.db.commit()
        return True

class StreakEventRepository:
    """Repository for StreakEvent operations"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def log_event(self, user_id: str, event_type: str, streak_count: int, 
                  previous_streak: int = 0, metadata: Dict = None) -> StreakEvent:
        """Log a streak event"""
        event = StreakEvent(
            user_id=user_id,
            event_type=event_type,
            streak_count=streak_count,
            previous_streak=previous_streak,
            meta_info=metadata or {}   # ✅ matches the model
        )

        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event
    
    def get_user_events(self, user_id: str, limit: int = 50) -> List[StreakEvent]:
        """Get user's streak events"""
        return self.db.query(StreakEvent)\
                     .filter(StreakEvent.user_id == user_id)\
                     .order_by(StreakEvent.created_at.desc())\
                     .limit(limit)\
                     .all()

class JournalRepository:
    """Repository for Journal entries in MongoDB"""
    
    def __init__(self, collection):
        self.collection = collection
    
    def save_entry(self, user_id: str, content: str, analysis_result: Dict, 
                   inspiration: str, eco_tags: List[str]) -> str:
        """Save journal entry to MongoDB"""
        entry = {
            "_id": ObjectId(),
            "user_id": user_id,
            "content": content,
            "analysis": analysis_result,
            "inspiration": inspiration,
            "eco_tags": eco_tags,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = self.collection.insert_one(entry)
        return str(result.inserted_id)
    
    def get_user_entries(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get user's journal entries"""
        entries = self.collection.find(
            {"user_id": user_id}
        ).sort("created_at", -1).limit(limit)
        
        return [self._convert_objectid(entry) for entry in entries]
    
    def get_entry_by_id(self, entry_id: str) -> Optional[Dict]:
        """Get specific journal entry"""
        entry = self.collection.find_one({"_id": ObjectId(entry_id)})
        return self._convert_objectid(entry) if entry else None
    
    def _convert_objectid(self, entry: Dict) -> Dict:
        """Convert ObjectId to string for JSON serialization"""
        if entry and "_id" in entry:
            entry["_id"] = str(entry["_id"])
        return entry

# Achievement definitions
ACHIEVEMENTS = {
    "first_entry": {
        "name": "First Step",
        "description": "Created your first eco-journal entry",
        "badge": "🌱",
        "streak_required": 1
    },
    "week_warrior": {
        "name": "Week Warrior",
        "description": "Maintained streak for 7 days",
        "badge": "🔥",
        "streak_required": 7
    },
    "month_champion": {
        "name": "Month Champion", 
        "description": "Maintained streak for 30 days",
        "badge": "🏆",
        "streak_required": 30
    },
    "quarter_guardian": {
        "name": "Quarter Guardian",
        "description": "Maintained streak for 90 days", 
        "badge": "🌿",
        "streak_required": 90
    },
    "year_legend": {
        "name": "Year Legend",
        "description": "Maintained streak for 365 days",
        "badge": "🌍",
        "streak_required": 365
    }
}

class AchievementRepository:
    """Repository for Achievement operations"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def award_achievement(self, user_id: str, achievement_key: str, streak_count: int) -> Achievement:
        """Award achievement to user"""
        achievement_info = ACHIEVEMENTS[achievement_key]
        
        achievement = Achievement(
            user_id=user_id,
            achievement_type=achievement_key,
            achievement_name=achievement_info["name"],
            description=achievement_info["description"],
            badge_emoji=achievement_info["badge"],
            streak_count_when_earned=streak_count
        )
        
        self.db.add(achievement)
        self.db.commit()
        self.db.refresh(achievement)
        return achievement
    
    def get_user_achievements(self, user_id: str) -> List[Achievement]:
        """Get all user achievements"""
        return self.db.query(Achievement)\
                     .filter(Achievement.user_id == user_id)\
                     .order_by(Achievement.earned_at.desc())\
                     .all()
    
    def check_and_award_achievements(self, user_id: str, current_streak: int) -> List[Achievement]:
        """Check and award any new achievements"""
        existing_achievements = {
            a.achievement_type for a in self.get_user_achievements(user_id)
        }
        
        new_achievements = []
        for key, info in ACHIEVEMENTS.items():
            if (key not in existing_achievements and 
                current_streak >= info["streak_required"]):
                achievement = self.award_achievement(user_id, key, current_streak)
                new_achievements.append(achievement)
        
        return new_achievements

# Initialize database manager

# Import User model so SQLAlchemy knows about it
from backend.Auth.models import User

# Create all tables in the database
Base.metadata.create_all(bind=engine)
db_manager = DatabaseManager()

# Factory functions for repositories
def get_user_repository() -> UserRepository:
    return UserRepository(db_manager.get_postgres_session())

def get_streak_event_repository() -> StreakEventRepository:
    return StreakEventRepository(db_manager.get_postgres_session())

def get_journal_repository() -> JournalRepository:
    return JournalRepository(db_manager.mongo_collection)

def get_achievement_repository() -> AchievementRepository:
    return AchievementRepository(db_manager.get_postgres_session())


# Function to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()