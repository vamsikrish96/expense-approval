from fastapi import Request
from models import User
from services.auth_service import get_user_from_auth_header


async def get_current_user(request: Request) -> User:
    auth_header = request.headers.get("authorization")
    return get_user_from_auth_header(auth_header)
