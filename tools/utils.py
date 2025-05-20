import os
import requests
from dotenv import load_dotenv

load_dotenv()

class AdtError(Exception):
    """Wraps ADT HTTP errors with status and message."""
    def __init__(self, status_code: int, message: str):
        super().__init__(f"ADT Error {status_code}: {message}")
        self.status_code = status_code

# Load global SAP connection settings once
SAP_URL    = os.getenv("SAP_URL")
print(SAP_URL)
SAP_CLIENT = os.getenv("SAP_CLIENT")
SAP_USER   = os.getenv("SAP_USER")
SAP_PASS   = os.getenv("SAP_PASS")
VERIFY_SSL = os.getenv("SAP_VERIFY_SSL", "true").lower() == "true"
TIMEOUT    = int(os.getenv("SAP_TIMEOUT", "30"))

if not all([SAP_URL, SAP_CLIENT, SAP_USER, SAP_PASS]):
    raise EnvironmentError(
        "Please set SAP_URL, SAP_CLIENT, SAP_USER, and SAP_PASS environment variables"
    )


def make_session() -> requests.Session:
    """
    Creates and configures a requests.Session for ADT calls using global settings.
    """
    session = requests.Session()
    session.auth = (SAP_USER, SAP_PASS)
    session.verify = VERIFY_SSL
    session.params = {"sap-client": SAP_CLIENT}
    session.timeout = TIMEOUT
    return session