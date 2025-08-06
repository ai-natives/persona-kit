"""
Simple authentication for API endpoints.

This is a placeholder implementation. In production, you would
implement proper authentication with JWT tokens, OAuth, etc.
"""

from typing import Dict
from fastapi import HTTPException, Header


async def get_current_user(
    authorization: str | None = Header(None)
) -> Dict[str, str]:
    """
    Get the current authenticated user.
    
    This is a simplified implementation for v0.1.
    In production, this would validate JWT tokens or API keys.
    
    Args:
        authorization: Authorization header value
        
    Returns:
        User information dictionary
        
    Raises:
        HTTPException: If authentication fails
    """
    # For v0.1, we'll accept any authorization header
    # In production, validate JWT/API key here
    if authorization:
        # Extract username from header (simplified)
        # Format: "Bearer <username>" or "ApiKey <username>"
        parts = authorization.split(" ", 1)
        if len(parts) == 2:
            return {
                "username": parts[1],
                "auth_type": parts[0].lower()
            }
    
    # For v0.1, allow unauthenticated access with default user
    return {
        "username": "default_user",
        "auth_type": "none"
    }