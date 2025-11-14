"""
MinIO Storage Service for handling image uploads and deletions.
"""
import os
import uuid
from typing import Optional
import boto3
from botocore.exceptions import ClientError
from django.conf import settings


class MinIOStorage:
    """Service class for interacting with MinIO object storage."""
    
    def __init__(self):
        """Initialize MinIO client with settings from environment."""
        self.endpoint = os.getenv('MINIO_ENDPOINT', 'minio:9000')
        self.access_key = os.getenv('MINIO_ACCESS_KEY', 'minio')
        self.secret_key = os.getenv('MINIO_SECRET_KEY', 'mino_admin')
        self.bucket_name = 'social-media-bucket'
        
        # Create S3 client (MinIO is S3-compatible)
        self.client = boto3.client(
            's3',
            endpoint_url=f'http://{self.endpoint}',
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name='us-east-1'  # MinIO needs a region
        )
        
        # Ensure bucket exists
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Create bucket if it doesn't exist."""
        try:
            self.client.head_bucket(Bucket=self.bucket_name)
        except ClientError:
            # Bucket doesn't exist, create it
            try:
                self.client.create_bucket(Bucket=self.bucket_name)
                print(f"Created bucket: {self.bucket_name}")
            except ClientError as e:
                print(f"Error creating bucket: {e}")
    
    def upload_image(self, file, folder: str = 'posts') -> Optional[str]:
        """
        Upload an image file to MinIO.
        
        Args:
            file: Django UploadedFile object
            folder: Folder path in bucket (default: 'posts')
        
        Returns:
            str: URL path to the uploaded image, or None if upload failed
        """
        try:
            # Generate unique filename
            ext = file.name.split('.')[-1] if '.' in file.name else 'jpg'
            filename = f"{folder}/{uuid.uuid4()}.{ext}"
            
            # Upload file
            self.client.upload_fileobj(
                file,
                self.bucket_name,
                filename,
                ExtraArgs={'ContentType': file.content_type}
            )
            
            # Return the path (URL will be constructed when serving)
            return filename
            
        except ClientError as e:
            print(f"Error uploading image: {e}")
            return None
    
    def delete_image(self, image_path: str) -> bool:
        """
        Delete an image from MinIO.
        
        Args:
            image_path: Path to the image in the bucket
        
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            self.client.delete_object(
                Bucket=self.bucket_name,
                Key=image_path
            )
            return True
        except ClientError as e:
            print(f"Error deleting image: {e}")
            return False
    
    def get_image_url(self, image_path: str) -> str:
        """
        Get the full URL for an image.
        
        Args:
            image_path: Path to the image in the bucket
        
        Returns:
            str: Full URL to access the image
        """
        return f"http://{self.endpoint}/{self.bucket_name}/{image_path}"


# Global instance
minio_storage = MinIOStorage()
