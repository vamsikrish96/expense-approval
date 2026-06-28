from fastapi import APIRouter, Depends, status
from uuid import UUID
from typing import Optional

from models import ExpenseCreate, ExpenseUpdate, Expense, User
from api.middleware import get_current_user
from services.expense_service import ExpenseService
from database import InMemoryDatabase

router = APIRouter(prefix="/expenses", tags=["expenses"])


def get_db() -> InMemoryDatabase:
    from main import db
    return db


def get_expense_service(db: InMemoryDatabase = Depends(get_db)) -> ExpenseService:
    return ExpenseService(db)


@router.post("", status_code=status.HTTP_201_CREATED)
async def submit_expense(
    expense: ExpenseCreate,
    user: User = Depends(get_current_user),
    service: ExpenseService = Depends(get_expense_service),
) -> Expense:
    return service.submit_expense(
        user=user,
        amount=expense.amount,
        category=expense.category,
        description=expense.description,
        expense_date=expense.expense_date,
    )


@router.get("", status_code=status.HTTP_200_OK)
async def list_expenses(
    user: User = Depends(get_current_user),
    service: ExpenseService = Depends(get_expense_service),
) -> list[Expense]:
    return service.list_expenses(user)


@router.get("/{expense_id}", status_code=status.HTTP_200_OK)
async def get_expense(
    expense_id: UUID,
    user: User = Depends(get_current_user),
    service: ExpenseService = Depends(get_expense_service),
) -> Expense:
    return service.get_expense(expense_id, user)


@router.patch("/{expense_id}/approve", status_code=status.HTTP_200_OK)
async def approve_expense(
    expense_id: UUID,
    user: User = Depends(get_current_user),
    service: ExpenseService = Depends(get_expense_service),
) -> Expense:
    return service.approve_expense(expense_id, user)


@router.patch("/{expense_id}/reject", status_code=status.HTTP_200_OK)
async def reject_expense(
    expense_id: UUID,
    reason: Optional[str] = None,
    user: User = Depends(get_current_user),
    service: ExpenseService = Depends(get_expense_service),
) -> Expense:
    return service.reject_expense(expense_id, user, reason)


@router.patch("/{expense_id}/process", status_code=status.HTTP_200_OK)
async def process_expense(
    expense_id: UUID,
    user: User = Depends(get_current_user),
    service: ExpenseService = Depends(get_expense_service),
) -> Expense:
    return service.process_expense(expense_id, user)


@router.patch("/{expense_id}/resubmit", status_code=status.HTTP_200_OK)
async def resubmit_expense(
    expense_id: UUID,
    expense: ExpenseUpdate,
    user: User = Depends(get_current_user),
    service: ExpenseService = Depends(get_expense_service),
) -> Expense:
    return service.resubmit_expense(
        expense_id=expense_id,
        user=user,
        amount=expense.amount,
        category=expense.category,
        description=expense.description,
        expense_date=expense.expense_date,
    )


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense(
    expense_id: UUID,
    user: User = Depends(get_current_user),
    service: ExpenseService = Depends(get_expense_service),
) -> None:
    service.delete_expense(expense_id, user)
