import re
import logging
from typing import Tuple, Optional

# Configure structured logging
logger = logging.getLogger("ai_devops_mcp")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(levelname)s] %(asctime)s - %(name)s - %(message)s", datefmt="%H:%M:%S")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

def parse_github_url(url: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extracts (owner, repo) from a GitHub repository URL or string like 'owner/repo'.
    Examples:
      - https://github.com/facebook/react -> ('facebook', 'react')
      - https://github.com/facebook/react.git -> ('facebook', 'react')
      - facebook/react -> ('facebook', 'react')
    """
    if not url:
        return None, None
    url = url.strip().rstrip("/")
    if url.endswith(".git"):
        url = url[:-4]
    
    # Check if format is owner/repo
    parts = url.split("/")
    if len(parts) >= 2:
        owner = parts[-2]
        repo = parts[-1]
        if owner.lower() in ("undefined", "null", "") or repo.lower() in ("undefined", "null", ""):
            return None, None
        return owner, repo
    return None, None

def sanitize_log_message(msg: str) -> str:
    """Mask any potential tokens or secrets from logs."""
    # Mask github tokens (ghp_..., github_pat_...)
    msg = re.sub(r'ghp_[a-zA-Z0-9]{36}', 'ghp_***MASKED***', msg)
    msg = re.sub(r'github_pat_[a-zA-Z0-9_]{40,}', 'github_pat_***MASKED***', msg)
    # Mask generic authorization headers or API keys
    msg = re.sub(r'(Bearer\s+)[a-zA-Z0-9_\-\.]{15,}', r'\1***MASKED***', msg)
    return msg
