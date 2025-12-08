"""
Keycloak Authentication Backend for Django REST Framework

This module provides authentication integration between Keycloak and Django,
automatically syncing users from Keycloak tokens to the Django database.
"""

import logging
from typing import Optional, Tuple
from datetime import datetime

from django.conf import settings
from rest_framework import authentication, exceptions
from jose import jwt, JWTError
import requests

from .models import User

logger = logging.getLogger(__name__)


class KeycloakAuthentication(authentication.BaseAuthentication):
    """
    Authenticate users using Keycloak JWT tokens.
    
    This authentication backend:
    1. Validates the JWT token from Keycloak
    2. Extracts user information from the token
    3. Syncs the user to Django's database (creates or updates)
    4. Returns the Django User object for use in views
    """
    
    def __init__(self):
        self.keycloak_server_url = getattr(settings, 'KEYCLOAK_SERVER_URL', 'http://keycloak:8080')
        self.keycloak_realm = getattr(settings, 'KEYCLOAK_REALM', 'social-media-realm')
        self.keycloak_client_id = getattr(settings, 'KEYCLOAK_CLIENT_ID', 'social-media-backend-client')
        self._public_key = None
    
    def get_keycloak_public_key(self) -> str:
        """
        Fetch Keycloak's public key for JWT verification.
        This is cached after the first request.
        """
        if self._public_key:
            return self._public_key
            
        try:
            # Fetch the public key from Keycloak's well-known endpoint
            certs_url = f"{self.keycloak_server_url}/realms/{self.keycloak_realm}/protocol/openid-connect/certs"
            response = requests.get(certs_url, timeout=5)
            response.raise_for_status()
            
            keys = response.json()
            # Use the first key (in production, match by 'kid')
            if keys.get('keys'):
                key_data = keys['keys'][0]
                # Construct PEM format public key
                self._public_key = f"-----BEGIN PUBLIC KEY-----\n{key_data['x5c'][0]}\n-----END PUBLIC KEY-----"
                return self._public_key
            
            raise Exception("No keys found in Keycloak certificate endpoint")
            
        except Exception as e:
            logger.error(f"Failed to fetch Keycloak public key: {e}")
            raise exceptions.AuthenticationFailed("Unable to verify token - Keycloak unavailable")
    
    def authenticate(self, request) -> Optional[Tuple[User, str]]:
        """
        Authenticate the request using the Authorization header.
        
        Returns:
            Tuple of (User, token) if authentication succeeds
            None if no authentication was attempted
            
        Raises:
            AuthenticationFailed if authentication was attempted but failed
        """
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header:
            return None  # No authentication attempted
        
        # Extract Bearer token
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return None
        
        token = parts[1]
        
        try:
            # Decode and verify the JWT token
            decoded_token = self.verify_token(token)
            
            # Extract user information from token
            user = self.get_or_create_user(decoded_token)
            
            return (user, token)
            
        except JWTError as e:
            logger.warning(f"JWT verification failed: {e}")
            raise exceptions.AuthenticationFailed("Invalid or expired token")
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise exceptions.AuthenticationFailed("Authentication failed")
    
    def verify_token(self, token: str) -> dict:
        """
        Verify and decode the JWT token using Keycloak's public key.
        
        Args:
            token: The JWT token string
            
        Returns:
            Decoded token payload as dictionary
            
        Raises:
            JWTError if token is invalid or expired
        """
        public_key = self.get_keycloak_public_key()
        
        # Verify token signature and decode
        decoded = jwt.decode(
            token,
            public_key,
            algorithms=['RS256'],
            audience=self.keycloak_client_id,
            options={
                'verify_signature': True,
                'verify_aud': True,
                'verify_exp': True,
            }
        )
        
        return decoded
    
    def get_or_create_user(self, token_data: dict) -> User:
        """
        Get or create a Django user based on Keycloak token data.
        
        This method syncs the user from Keycloak to Django's database,
        creating a new user if they don't exist or updating if they do.
        
        Args:
            token_data: Decoded JWT token containing user information
            
        Returns:
            User object
        """
        # Extract user information from token
        keycloak_id = token_data.get('sub')
        username = token_data.get('preferred_username')
        email = token_data.get('email', f"{username}@technikum-wien.at")
        name = token_data.get('name', username)
        
        # Additional custom claims (if configured in Keycloak)
        study_program = token_data.get('study_program', '')
        interests = token_data.get('interests', [])
        
        if not keycloak_id or not username:
            raise exceptions.AuthenticationFailed("Token missing required user information")
        
        # Get or create user
        user, created = User.objects.get_or_create(
            keycloak_id=keycloak_id,
            defaults={
                'username': username,
                'name': name,
                'email': email,
                'study_program': study_program,
                'interests': interests[:5] if isinstance(interests, list) else [],
                'last_login': datetime.now(),
            }
        )
        
        # Update existing user with latest info from Keycloak
        if not created:
            user.username = username
            user.name = name
            user.email = email
            user.study_program = study_program or user.study_program
            user.interests = interests[:5] if isinstance(interests, list) and interests else user.interests
            user.last_login = datetime.now()
            user.save()
        
        logger.info(f"User {'created' if created else 'updated'}: {username} (Keycloak ID: {keycloak_id})")
        
        return user
    
    def authenticate_header(self, request) -> str:
        """
        Return the WWW-Authenticate header value for 401 responses.
        """
        return 'Bearer realm="api"'
