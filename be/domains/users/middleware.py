"""
Middleware to attach authenticated Keycloak user to Django request.

This middleware works in conjunction with KeycloakAuthentication to ensure
that request.user is always populated with the authenticated user.
"""

import logging
from django.utils.deprecation import MiddlewareMixin
from domains.users.authentication import KeycloakAuthentication

logger = logging.getLogger(__name__)


class KeycloakUserMiddleware(MiddlewareMixin):
    """
    Middleware that populates request.user with the Keycloak-authenticated user.
    
    This runs after Django's authentication middleware and uses the
    KeycloakAuthentication backend to validate tokens and sync users.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.keycloak_auth = KeycloakAuthentication()
    
    def process_request(self, request):
        """
        Process the request and attach the authenticated user.
        """
        # Skip if user is already authenticated (e.g., by Django admin)
        if hasattr(request, 'user') and request.user and request.user.is_authenticated:
            return
        
        try:
            # Try to authenticate using Keycloak
            auth_result = self.keycloak_auth.authenticate(request)
            
            if auth_result:
                user, token = auth_result
                request.user = user
                request.auth = token
                logger.debug(f"Keycloak user authenticated: {user.username}")
        except Exception as e:
            # Log but don't fail the request
            logger.debug(f"Keycloak authentication skipped: {e}")
            pass
