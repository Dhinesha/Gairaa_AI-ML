import pytest
import sys
from pathlib import Path

# Add parent directory to path so auth module can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from auth import authenticate_user

def test_login_success():
    """Verify admin login succeeds with status 200."""
    response = authenticate_user("admin", "AdminSecret123!")
    assert response["status_code"] == 200
    assert "token" in response
    assert response["user"] == "admin"

def test_login_empty_username():
    """Verify empty username returns status 400."""
    response = authenticate_user("", "somepassword")
    assert response["status_code"] == 400
    assert "error" in response

def test_login_invalid_password():
    """
    Verify invalid password returns 401 Unauthorized.
    Intentional failure: authenticate_user raises unhandled ValueError on 'invalid' or 'wrong_password',
    failing the assertion or crashing.
    """
    response = authenticate_user("admin", "invalid")
    assert response["status_code"] == 401, f"Expected 401 but received {response.get('status_code', 500)}"
