"""Database service layer for the SWEG project."""

import os
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker, joinedload
from typing import List, Optional
from .models import Base, User, Post


class DatabaseService:
    """Service class for database operations."""
    
    def __init__(self, database_url: str = None):
        """Initialize the database service.
        
        Args:
            database_url: Database connection URL. If None, uses posts.db in the be directory.
        """
        if database_url is None:
            # Always use the be directory for the database
            current_dir = os.path.dirname(os.path.abspath(__file__))
            be_dir = os.path.dirname(os.path.dirname(current_dir))
            db_path = os.path.join(be_dir, "posts.db")
            database_url = f"sqlite:///{db_path}"
        
        self.engine = create_engine(database_url, echo=False)
        self.Session = sessionmaker(bind=self.engine)
        self.create_tables()
    
    def create_tables(self):
        """Create all tables in the database."""
        Base.metadata.create_all(self.engine)
    
    def create_user(self, username: str, email: str) -> User:
        """Create a new user.
        
        Args:
            username: User's username
            email: User's email
            
        Returns:
            Created User object
        """
        with self.Session() as session:
            user = User(username=username, email=email)
            session.add(user)
            session.commit()
            session.refresh(user)
            return user
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a user by username.
        
        Args:
            username: User's username
            
        Returns:
            User object if found, None otherwise
        """
        with self.Session() as session:
            return session.query(User).filter(User.username == username).first()
    
    def create_post(self, title: str, text: str, user_id: int, image: str = None) -> Post:
        """Create a new post.
        
        Args:
            title: Post title
            text: Post content
            user_id: ID of the user creating the post
            image: Optional image URL or path
            
        Returns:
            Created Post object
        """
        with self.Session() as session:
            post = Post(title=title, text=text, user_id=user_id, image=image)
            session.add(post)
            session.commit()
            session.refresh(post)
            return post
    
    def get_latest_post(self) -> Optional[Post]:
        """Get the latest post.
        
        Returns:
            Latest Post object with user information!!!, None if no posts exist
        """
        with self.Session() as session:
            post = session.query(Post).options(
                joinedload(Post.user)
            ).order_by(desc(Post.created_at)).first()
            
            if post:
                # Detach from session to avoid issues
                session.expunge(post)
                if post.user and post.user in session:
                    session.expunge(post.user)
            
            return post
    
    def get_all_posts(self) -> List[Post]:
        """Get all posts ordered by creation date (newest first).
        
        Returns:
            List of Post objects with user information
        """
        with self.Session() as session:
            posts = session.query(Post).options(
                joinedload(Post.user)
            ).order_by(desc(Post.created_at)).all()
            
            # Detach from session
            for post in posts:
                session.expunge(post)
                if post.user and post.user in session:
                    session.expunge(post.user)
            
            return posts
    
    def get_posts_by_user(self, user_id: int) -> List[Post]:
        """Get all posts by a specific user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of Post objects by the user
        """
        with self.Session() as session:
            posts = session.query(Post).options(
                joinedload(Post.user)
            ).filter(Post.user_id == user_id).order_by(desc(Post.created_at)).all()
            
            # Detach from session
            for post in posts:
                session.expunge(post)
                if post.user and post.user in session:
                    session.expunge(post.user)
            
            return posts