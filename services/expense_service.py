from datetime import date
from uuid import UUID
from typing import Optional

from models import Expense, AuditAction, User, UserRole
from database import InMemoryDatabase
from api.exceptions import (
    SelfApprovalError,
    NotFoundError,
    ForbiddenError,
    StateTransitionError,
)


class ExpenseService:
    def __init__(self, db: InMemoryDatabase):
        self.db = db

    def submit_expense(
        self,
        user: User,
        amount: float,
        category: str,
        description: str,
        expense_date: date,
    ) -> Expense:
        expense = self.db.create_expense(
            employee_id=user.oid,
            amount=amount,
            category=category,
            description=description,
            expense_date=expense_date,
        )

        self.db.create_audit_log(
            expense_id=expense.id,
            action=AuditAction.SUBMITTED,
            actor_id=user.oid,
            new_state=expense.model_dump(),
        )

        return expense

    def get_expense(self, expense_id: UUID, user: User) -> Expense:
        expense = self.db.get_expense_or_raise(expense_id)
        self._check_expense_access(expense, user)
        return expense

    def list_expenses(self, user: User) -> list[Expense]:
        if user.has_manager_role or user.has_finance_role:
            return self.db.get_all_expenses()
        else:
            return self.db.get_expenses_by_employee(user.oid)

    def approve_expense(self, expense_id: UUID, user: User) -> Expense:
        if not user.has_manager_role:
            raise ForbiddenError("Only managers can approve expenses")

        expense = self.db.get_expense_or_raise(expense_id)

        if expense.employee_id == user.oid:
            raise SelfApprovalError()

        previous_state = expense.model_dump()
        updated_expense = self.db.approve_expense(expense_id, user.oid)

        self.db.create_audit_log(
            expense_id=expense_id,
            action=AuditAction.APPROVED,
            actor_id=user.oid,
            previous_state=previous_state,
            new_state=updated_expense.model_dump(),
        )

        return updated_expense

    def reject_expense(self, expense_id: UUID, user: User, reason: Optional[str] = None) -> Expense:
        if not user.has_manager_role:
            raise ForbiddenError("Only managers can reject expenses")

        expense = self.db.get_expense_or_raise(expense_id)

        if expense.employee_id == user.oid:
            raise SelfApprovalError()

        previous_state = expense.model_dump()
        updated_expense = self.db.reject_expense(expense_id, user.oid, reason)

        self.db.create_audit_log(
            expense_id=expense_id,
            action=AuditAction.REJECTED,
            actor_id=user.oid,
            previous_state=previous_state,
            new_state=updated_expense.model_dump(),
            reason=reason,
        )

        return updated_expense

    def process_expense(self, expense_id: UUID, user: User) -> Expense:
        if not user.has_finance_role:
            raise ForbiddenError("Only finance can process expenses")

        expense = self.db.get_expense_or_raise(expense_id)
        previous_state = expense.model_dump()
        updated_expense = self.db.process_expense(expense_id, user.oid)

        self.db.create_audit_log(
            expense_id=expense_id,
            action=AuditAction.PROCESSED,
            actor_id=user.oid,
            previous_state=previous_state,
            new_state=updated_expense.model_dump(),
        )

        return updated_expense

    def resubmit_expense(
        self,
        expense_id: UUID,
        user: User,
        amount: float,
        category: str,
        description: str,
        expense_date: date,
    ) -> Expense:
        expense = self.db.get_expense_or_raise(expense_id)

        if expense.employee_id != user.oid:
            raise ForbiddenError("You can only resubmit your own expenses")

        previous_state = expense.model_dump()
        updated_expense = self.db.resubmit_expense(
            expense_id, amount, category, description, expense_date
        )

        self.db.create_audit_log(
            expense_id=expense_id,
            action=AuditAction.RESUBMITTED,
            actor_id=user.oid,
            previous_state=previous_state,
            new_state=updated_expense.model_dump(),
        )

        return updated_expense

    def delete_expense(self, expense_id: UUID, user: User) -> None:
        expense = self.db.get_expense_or_raise(expense_id)

        if expense.employee_id != user.oid:
            raise ForbiddenError("You can only delete your own expenses")

        previous_state = expense.model_dump()
        self.db.delete_expense(expense_id)

        self.db.create_audit_log(
            expense_id=expense_id,
            action=AuditAction.DELETED,
            actor_id=user.oid,
            previous_state=previous_state,
        )

    def get_audit_logs(self) -> list:
        return self.db.get_audit_logs()

    def get_expense_audit_log(self, expense_id: UUID, user: User) -> list:
        expense = self.db.get_expense_or_raise(expense_id)
        self._check_expense_access(expense, user)
        return self.db.get_audit_logs_by_expense(expense_id)

    def _check_expense_access(self, expense: Expense, user: User) -> None:
        is_owner = expense.employee_id == user.oid
        is_manager_or_finance = user.has_manager_role or user.has_finance_role

        if not is_owner and not is_manager_or_finance:
            raise ForbiddenError("You do not have access to this expense")
