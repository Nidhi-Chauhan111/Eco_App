#SQLAlchemy User model

import sys, os
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

# Add parent directory (backend) to sys.path
#sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Base from Journal
#from Database.Journal import Base
from Database.db import Base



class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    password = Column(String(255), nullable=False)

    # Relationships to other models
    #from Database.Journal import UserStats
    stats = relationship("UserStats", back_populates="user", cascade="all, delete-orphan", uselist=False)
    streak_events = relationship("StreakEvent", back_populates="user", cascade="all, delete-orphan")
    achievements = relationship("Achievement", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(username={self.username}, email={self.email})>"