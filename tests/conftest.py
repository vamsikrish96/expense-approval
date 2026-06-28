import pytest
from datetime import date, timedelta
from services.auth_service import create_fake_jwt_token
from database import InMemoryDatabase
import main


@pytest.fixture
def test_db():
    main.db = InMemoryDatabase()
    return main.db


@pytest.fixture
def employee_token():
    return create_fake_jwt_token(
        oid="emp-001",
        preferred_username="employee@company.com",
        name="John Employee",
        roles=["employee"],
    )


@pytest.fixture
def manager_token():
    return create_fake_jwt_token(
        oid="mgr-001",
        preferred_username="manager@company.com",
        name="Jane Manager",
        roles=["manager"],
    )


@pytest.fixture
def finance_token():
    return create_fake_jwt_token(
        oid="fin-001",
        preferred_username="finance@company.com",
        name="Bob Finance",
        roles=["finance"],
    )


@pytest.fixture
def valid_expense_data():
    return {
        "amount": 500.00,
        "category": "TRAVEL",
        "description": "Conference attendance in New York",
        "expense_date": (date.today() - timedelta(days=5)).isoformat(),
    }


@pytest.fixture
def auth_headers(employee_token):
    return {"Authorization": f"Bearer {employee_token}"}
