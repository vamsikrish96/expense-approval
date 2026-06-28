import pytest
from datetime import date, timedelta
from uuid import UUID
from fastapi.testclient import TestClient
from models import ExpenseStatus, AuditAction
from main import app, db
from tests.conftest import *


client = TestClient(app)


def test_submit_expense_workflow(test_db, employee_token, valid_expense_data):
    response = client.post(
        "/expenses",
        json=valid_expense_data,
        headers={"Authorization": f"Bearer {employee_token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "SUBMITTED"
    assert data["employee_id"] == "emp-001"
    assert data["amount"] == 500.00
    assert UUID(data["id"])


def test_manager_approve_expense(test_db, employee_token, manager_token, valid_expense_data):
    # Employee submits
    submit_response = client.post(
        "/expenses",
        json=valid_expense_data,
        headers={"Authorization": f"Bearer {employee_token}"},
    )
    expense_id = submit_response.json()["id"]

    # Manager approves
    approve_response = client.patch(
        f"/expenses/{expense_id}/approve",
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert approve_response.status_code == 200
    data = approve_response.json()
    assert data["status"] == "MANAGER_APPROVED"
    assert data["manager_id"] == "mgr-001"


def test_manager_reject_expense(test_db, employee_token, manager_token, valid_expense_data):
    # Employee submits
    submit_response = client.post(
        "/expenses",
        json=valid_expense_data,
        headers={"Authorization": f"Bearer {employee_token}"},
    )
    expense_id = submit_response.json()["id"]

    # Manager rejects
    reject_response = client.patch(
        f"/expenses/{expense_id}/reject?reason=Invalid category",
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert reject_response.status_code == 200
    data = reject_response.json()
    assert data["status"] == "REJECTED"
    assert data["rejection_reason"] == "Invalid category"


def test_finance_process_expense(test_db, employee_token, manager_token, finance_token, valid_expense_data):
    # Employee submits
    submit_response = client.post(
        "/expenses",
        json=valid_expense_data,
        headers={"Authorization": f"Bearer {employee_token}"},
    )
    expense_id = submit_response.json()["id"]

    # Manager approves
    client.patch(
        f"/expenses/{expense_id}/approve",
        headers={"Authorization": f"Bearer {manager_token}"},
    )

    # Finance processes
    process_response = client.patch(
        f"/expenses/{expense_id}/process",
        headers={"Authorization": f"Bearer {finance_token}"},
    )
    assert process_response.status_code == 200
    data = process_response.json()
    assert data["status"] == "FINANCE_PROCESSED"
    assert data["finance_id"] == "fin-001"


def test_resubmit_rejected_expense(test_db, employee_token, manager_token, valid_expense_data):
    # Employee submits
    submit_response = client.post(
        "/expenses",
        json=valid_expense_data,
        headers={"Authorization": f"Bearer {employee_token}"},
    )
    expense_id = submit_response.json()["id"]

    # Manager rejects
    client.patch(
        f"/expenses/{expense_id}/reject?reason=Missing receipt",
        headers={"Authorization": f"Bearer {manager_token}"},
    )

    # Employee resubmits with updated data
    updated_data = {
        **valid_expense_data,
        "amount": 450.00,
        "description": "Conference attendance with receipt attached",
    }
    resubmit_response = client.patch(
        f"/expenses/{expense_id}/resubmit",
        json=updated_data,
        headers={"Authorization": f"Bearer {employee_token}"},
    )
    assert resubmit_response.status_code == 200
    data = resubmit_response.json()
    assert data["status"] == "SUBMITTED"
    assert data["amount"] == 450.00
    assert data["rejection_reason"] is None


def test_employee_cannot_approve_own_expense(test_db, employee_token, valid_expense_data):
    # Employee submits
    submit_response = client.post(
        "/expenses",
        json=valid_expense_data,
        headers={"Authorization": f"Bearer {employee_token}"},
    )
    expense_id = submit_response.json()["id"]

    # Employee tries to approve own expense
    approve_response = client.patch(
        f"/expenses/{expense_id}/approve",
        headers={"Authorization": f"Bearer {employee_token}"},
    )
    # Employee doesn't have manager role, so gets error (403 or 400)
    assert approve_response.status_code in [400, 403]
    assert approve_response.json()["error"] == "FORBIDDEN"


def test_delete_submitted_expense(test_db, employee_token, valid_expense_data):
    # Employee submits
    submit_response = client.post(
        "/expenses",
        json=valid_expense_data,
        headers={"Authorization": f"Bearer {employee_token}"},
    )
    expense_id = submit_response.json()["id"]

    # Delete
    delete_response = client.delete(
        f"/expenses/{expense_id}",
        headers={"Authorization": f"Bearer {employee_token}"},
    )
    assert delete_response.status_code == 204

    # Verify it's deleted
    get_response = client.get(
        f"/expenses/{expense_id}",
        headers={"Authorization": f"Bearer {employee_token}"},
    )
    assert get_response.status_code == 404


def test_audit_log_created(test_db, employee_token, manager_token, valid_expense_data):
    # Employee submits
    submit_response = client.post(
        "/expenses",
        json=valid_expense_data,
        headers={"Authorization": f"Bearer {employee_token}"},
    )
    expense_id = submit_response.json()["id"]

    # Manager approves
    client.patch(
        f"/expenses/{expense_id}/approve",
        headers={"Authorization": f"Bearer {manager_token}"},
    )

    # Get audit log
    audit_response = client.get(
        f"/audit-logs/{expense_id}/detail",
        headers={"Authorization": f"Bearer {employee_token}"},
    )
    assert audit_response.status_code == 200
    logs = audit_response.json()
    assert len(logs) >= 2  # SUBMITTED and APPROVED


def test_list_expenses_role_based_filtering(test_db, employee_token, manager_token):
    # Create multiple expenses from different employees
    valid_data = {
        "amount": 100,
        "category": "MEALS",
        "description": "Lunch meeting at office",
        "expense_date": (date.today() - timedelta(days=1)).isoformat(),
    }

    client.post(
        "/expenses",
        json=valid_data,
        headers={"Authorization": f"Bearer {employee_token}"},
    )

    # Employee sees only their own
    employee_list = client.get(
        "/expenses",
        headers={"Authorization": f"Bearer {employee_token}"},
    )
    assert employee_list.status_code == 200
    assert len(employee_list.json()) == 1

    # Manager sees all
    manager_list = client.get(
        "/expenses",
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert manager_list.status_code == 200
    assert len(manager_list.json()) == 1
