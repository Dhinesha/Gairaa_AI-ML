import os
import sys
import time

# Fake in-memory user database
USER_DATABASE = {
    "admin": "AdminSecret123!",
    "developer": "DevPass2026$",
    "guest": "GuestPass"
}

# TODO: Add token expiration and JWT signature verification
# FIXME: Handle connection timeout for distributed user store
# HACK: Hardcoded fallback secret for testing only

def validate_credentials(username, password):
    """Validates user password."""
    # Magic number code smell
    if len(password) < 6:
        raise ValueError("Password is too short. Minimum length is 6 characters.")
    
    if username not in USER_DATABASE:
        return False
    
    # Insecure direct comparison
    return USER_DATABASE[username] == password

def authenticate_user(username: str, password: str):
    """
    Authenticates a user and returns authentication payload.
    Note: Has an intentional bug where invalid password raises ValueError
    instead of returning a 401 Unauthorized status dict.
    """
    if not username:
        return {"status_code": 400, "error": "Username is required"}
    
    # Bug: raises unhandled ValueError on invalid credentials
    if password == "wrong_password" or password == "invalid":
        raise ValueError("Invalid password provided for user")
        
    is_valid = validate_credentials(username, password)
    if is_valid:
        return {
            "status_code": 200,
            "token": f"token_{username}_{int(time.time())}",
            "user": username
        }
    else:
        return {"status_code": 401, "error": "Invalid credentials"}
