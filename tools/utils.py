import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class AdtError(Exception):
    """Wraps ADT HTTP errors with status and message."""
    def __init__(self, status_code: int, message: str):
        super().__init__(f"ADT Error {status_code}: {message}")
        self.status_code = status_code

# Load global SAP connection settings once
SAP_URL    = os.getenv("SAP_URL")
SAP_CLIENT = os.getenv("SAP_CLIENT")
SAP_USER   = os.getenv("SAP_USER")
SAP_PASS   = os.getenv("SAP_PASS")
SAP_AUTH_TYPE = os.getenv("SAP_AUTH_TYPE", "basic").lower()
SAP_JWT_TOKEN = os.getenv("SAP_JWT_TOKEN")
VERIFY_SSL = os.getenv("SAP_VERIFY_SSL", "true").lower() == "true"
TIMEOUT    = int(os.getenv("SAP_TIMEOUT", "30"))


def validate_configuration():
    """
    Validate authentication configuration.
    Call this function before making SAP connections.
    """
    # Validate authentication configuration
    if SAP_AUTH_TYPE == "jwt":
        if not all([SAP_URL, SAP_JWT_TOKEN]):
            raise EnvironmentError(
                "For JWT authentication, please set SAP_URL and SAP_JWT_TOKEN environment variables"
            )
    elif SAP_AUTH_TYPE == "basic":
        if not all([SAP_URL, SAP_CLIENT, SAP_USER, SAP_PASS]):
            raise EnvironmentError(
                "For basic authentication, please set SAP_URL, SAP_CLIENT, SAP_USER, and SAP_PASS environment variables"
            )
    else:
        raise EnvironmentError(
            f"Unsupported authentication type: {SAP_AUTH_TYPE}. Supported types: 'basic', 'jwt'"
        )


def make_session():
    """
    Creates and configures a requests.Session for ADT calls using global settings.
    Supports both basic authentication and JWT token authentication.
    
    Note: This function imports requests only when needed to avoid import issues.
    """
    import requests  # Import only when needed
    
    # Validate configuration before creating session
    validate_configuration()
    
    session = requests.Session()
    session.verify = VERIFY_SSL
    session.timeout = TIMEOUT
    
    if SAP_AUTH_TYPE == "jwt":
        # Use JWT token authentication
        session.headers.update({
            "Authorization": f"Bearer {SAP_JWT_TOKEN}",
            "Content-Type": "application/xml",
            "Accept": "application/xml"
        })
    else:
        # Use basic authentication (default)
        session.auth = (SAP_USER, SAP_PASS)
        session.params = {"sap-client": SAP_CLIENT}
    
    return session