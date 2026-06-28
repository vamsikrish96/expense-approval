import pytest
from services.auth_service import (
    parse_bearer_token,
    extract_user_from_token,
    get_user_from_auth_header,
    create_fake_jwt_token,
)
from api.exceptions import InvalidTokenError, MissingTokenError


def test_create_fake_jwt_token():
    token = create_fake_jwt_token(
        oid="test-oid",
        preferred_username="test@company.com",
        name="Test User",
        roles=["employee"],
    )
    assert isinstance(token, str)
    assert token.count(".") == 2


def test_parse_bearer_token_valid(employee_token):
    payload = parse_bearer_token(f"Bearer {employee_token}")
    assert payload["oid"] == "emp-001"
    assert payload["preferred_username"] == "employee@company.com"


def test_parse_bearer_token_missing():
    with pytest.raises(MissingTokenError):
        parse_bearer_token(None)


def test_parse_bearer_token_invalid_format():
    with pytest.raises(InvalidTokenError):
        parse_bearer_token("InvalidFormat")


def test_extract_user_from_token(employee_token):
    payload = parse_bearer_token(f"Bearer {employee_token}")
    user = extract_user_from_token(payload)
    assert user.oid == "emp-001"
    assert user.preferred_username == "employee@company.com"
    assert "employee" in user.roles


def test_extract_user_missing_required_field():
    payload = {"oid": "test-oid"}
    with pytest.raises(InvalidTokenError):
        extract_user_from_token(payload)


def test_get_user_from_auth_header(employee_token):
    user = get_user_from_auth_header(f"Bearer {employee_token}")
    assert user.oid == "emp-001"


def test_get_user_from_auth_header_missing_token():
    with pytest.raises(MissingTokenError):
        get_user_from_auth_header(None)
