"""Main application module for the SWEG project."""

from .database import DatabaseService
from .models import User, Post


def demo_post_operations():
    """Demonstrate post management operations."""
    # Initialize database service (will use be/posts.db)
    db = DatabaseService()
    
    print("=== SWEG Project Post Management Demo ===\n")
    
    # Create or get a user
    user = create_or_get_user(db, "john_doe", "john@example.com")
    print(f"Using user: {user.username} (ID: {user.id})")
    
    # Create sample posts
    posts_data = [
        {
            "title": "My First Post",
            "text": "This is my first post on the platform!",
            "image": "https://example.com/image1.jpg"
        },
        {
            "title": "Learning Python",
            "text": "Today I learned about SQLAlchemy and database management.",
            "image": None
        },
        {
            "title": "Beautiful Sunset",
            "text": "Witnessed an amazing sunset today. Nature is incredible!",
            "image": "https://example.com/sunset.jpg"
        }
    ]
    
    # Create posts
    created_posts = []
    for post_data in posts_data:
        post = db.create_post(
            title=post_data["title"],
            text=post_data["text"],
            user_id=user.id,
            image=post_data["image"]
        )
        created_posts.append(post)
        print(f"Created post: '{post.title}'")
    
    print(f"\nCreated {len(created_posts)} posts")
    
    # Retrieve and display the latest post
    latest_post = db.get_latest_post()
    if latest_post:
        print(f"\n=== Latest Post ===")
        print(f"Title: {latest_post.title}")
        print(f"Text: {latest_post.text}")
        print(f"Author: {latest_post.user.username}")
        print(f"Image: {latest_post.image or 'No image'}")
        print(f"Created: {latest_post.created_at}")
    else:
        print("\nNo posts found!")
    
    # Display all posts
    all_posts = db.get_all_posts()
    print(f"\n=== All Posts ({len(all_posts)} total) ===")
    for i, post in enumerate(all_posts, 1):
        print(f"{i}. {post.title} by {post.user.username}")
        print(f"   {post.text[:50]}{'...' if len(post.text) > 50 else ''}")
        print(f"   Created: {post.created_at}")
        print()


def create_or_get_user(db: DatabaseService, username: str, email: str) -> User:
    """Create a new user or get existing one by username."""
    existing_user = db.get_user_by_username(username)
    if existing_user:
        return existing_user
    else:
        return db.create_user(username, email)



def main() -> None:
    """Main entry point for the application."""
    demo_post_operations()


if __name__ == "__main__":
    main()