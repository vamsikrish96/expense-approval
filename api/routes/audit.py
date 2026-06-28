from fastapi import APIRouter, Depends, status
from uuid import UUID

from models import AuditLog, User
from api.middleware import get_current_user
from services.expense_service import ExpenseService
from database import InMemoryDatabase

router = APIRouter(prefix="/audit-logs", tags=["audit"])


def get_db() -> InMemoryDatabase:
    from main import db
    return db


def get_expense_service(db: InMemoryDatabase = Depends(get_db)) -> ExpenseService:
    return ExpenseService(db)


@router.get("", status_code=status.HTTP_200_OK)
async def get_audit_logs(
    user: User = Depends(get_current_user),
    service: ExpenseService = Depends(get_expense_service),
) -> list[AuditLog]:
    return service.get_audit_logs()


@router.get("/{expense_id}/detail", status_code=status.HTTP_200_OK)
async def get_expense_audit_log(
    expense_id: UUID,
    user: User = Depends(get_current_user),
    service: ExpenseService = Depends(get_expense_service),
) -> list[AuditLog]:
    return service.get_expense_audit_log(expense_id, user)
