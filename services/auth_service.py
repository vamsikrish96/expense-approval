import json
import base64
from typing import Optional
from models import User
from api.exceptions import InvalidTokenError, MissingTokenError


def parse_bearer_token(auth_header: Optional[str]) -> dict:
    if not auth_header:
        raise MissingTokenError("Authorization header is missing")

    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise InvalidTokenError("Invalid authorization header format")

    token = parts[1]
    try:
        # Split JWT into parts
        token_parts = token.split(".")
        if len(token_parts) != 3:
            raise InvalidTokenError("Invalid token format")

        # Decode payload (add padding if needed)
        payload = token_parts[1]
        payload += "=" * (4 - len(payload) % 4)
        decoded = base64.urlsafe_b64decode(payload)
        payload_data = json.loads(decoded)
        return payload_data
    except Exception as e:
        raise InvalidTokenError(f"Failed to parse token: {str(e)}")


def extract_user_from_token(token_payload: dict) -> User:
    required_fields = ["oid", "preferred_username", "name"]
    for field in required_fields:
        if field not in token_payload:
            raise InvalidTokenError(f"Missing required field: {field}")

    roles = token_payload.get("roles", [])
    if not roles:
        raise InvalidTokenError("No roles found in token")

    return User(
        oid=token_payload["oid"],
        preferred_username=token_payload["preferred_username"],
        name=token_payload["name"],
        roles=roles,
    )


def get_user_from_auth_header(auth_header: Optional[str]) -> User:
    payload = parse_bearer_token(auth_header)
    return extract_user_from_token(payload)


def create_fake_jwt_token(
    oid: str, preferred_username: str, name: str, roles: list[str]
) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "oid": oid,
        "preferred_username": preferred_username,
        "name": name,
        "roles": roles,
    }

    # Encode header and payload
    header_encoded = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
    payload_encoded = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")

    # Create signature (simplified - just a hash for demo)
    signature = base64.urlsafe_b64encode(b"fake-signature").decode().rstrip("=")

    return f"{header_encoded}.{payload_encoded}.{signature}"
