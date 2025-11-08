"""Database models for the SWEG project."""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime
from zoneinfo import ZoneInfo

Base = declarative_base() # used to map classes to database tables 


def get_european_time():
    """Get current time in European timezone (Europe/Berlin)."""
    return datetime.now(ZoneInfo("Europe/Berlin")) 


class User(Base):
    """User model for storing user information."""
    
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=get_european_time)
    
    # Relationship to n posts
    posts = relationship("Post", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class Post(Base):
    """Post model for storing post information."""
    
    __tablename__ = 'posts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    text = Column(Text, nullable=False)
    image = Column(String(500))  # URL or path to image
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False) # showes alchemy that posts is the n-side of the relationship
    created_at = Column(DateTime, default=get_european_time)
    
    # Relationship to 1 user
    user = relationship("User", back_populates="posts")
    
    def __repr__(self):
        return f"<Post(id={self.id}, title='{self.title}', user_id={self.user_id})>"


def create_tables(engine):
    """Create all tables in the database."""
    Base.metadata.create_all(engine)

# sqlite:///posts.db legt eine SQLite-Datei im aktuellen Ordner an.
def get_engine(database_url="sqlite:///posts.db"):
    """Create and return a database engine."""
    return create_engine(database_url, echo=True)


def get_session_maker(engine):
    """Create and return a session maker."""
    return sessionmaker(bind=engine)