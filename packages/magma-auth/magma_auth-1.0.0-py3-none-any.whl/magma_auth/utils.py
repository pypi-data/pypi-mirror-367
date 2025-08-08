# Standard library imports
from datetime import datetime, timezone

# Third party imports
import jwt
import requests

# Project imports
from magma_auth.const import URL_VALIDATE_TOKEN


def validate_token(token: str, url: str = None) -> bool:
    """Validate token

    Args:
        token (str): token
        url (str, optional): url to validate

    Returns:
        bool: True if token is valid
    """
    headers = {"Authorization": "Bearer " + token}
    url = url or URL_VALIDATE_TOKEN

    try:
        response = requests.request("GET", url, headers=headers).json()
    except Exception as e:
        print(f"Error validating token: {e}")
        return False

    if "code" in response:
        if response["code"] == 419:
            return False

    return True


def decode_token(token: str = None) -> dict:
    """Decode token

    Args:
        token (str): Token to decode

    Returns:
        dict: Decoded token with keys: 'issued_at', 'expires_at', abd 'roles'
    """
    decoded = jwt.decode(token, options={"verify_signature": False})

    return {
        "issued_at": datetime.fromtimestamp(decoded["iat"], timezone.utc),
        "expired_at": datetime.fromtimestamp(decoded["exp"], timezone.utc),
        "roles": decoded["roles"] if "roles" in decoded.keys() else None,
    }
