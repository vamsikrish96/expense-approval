from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, List
from models import Expense, ExpenseStatus, AuditLog, AuditAction
from api.exceptions import NotFoundError, StateTransitionError


class InMemoryDatabase:
    def __init__(self):
        self.expenses: dict[UUID, Expense] = {}
        self.audit_logs: dict[UUID, AuditLog] = {}

    def create_expense(
        self,
        employee_id: str,
        amount: float,
        category: str,
        description: str,
        expense_date,
    ) -> Expense:
        expense_id = uuid4()
        expense = Expense(
            id=expense_id,
            employee_id=employee_id,
            amount=amount,
            category=category,
            description=description,
            expense_date=expense_date,
            submitted_at=datetime.utcnow(),
            status=ExpenseStatus.SUBMITTED,
        )
        self.expenses[expense_id] = expense
        return expense

    def get_expense(self, expense_id: UUID) -> Optional[Expense]:
        return self.expenses.get(expense_id)

    def get_expense_or_raise(self, expense_id: UUID) -> Expense:
        expense = self.get_expense(expense_id)
        if not expense:
            raise NotFoundError()
        return expense

    def get_expenses_by_employee(self, employee_id: str) -> List[Expense]:
        return [e for e in self.expenses.values() if e.employee_id == employee_id]

    def get_all_expenses(self) -> List[Expense]:
        return list(self.expenses.values())

    def get_expenses_by_status(self, status: ExpenseStatus) -> List[Expense]:
        return [e for e in self.expenses.values() if e.status == status]

    def update_expense(self, expense_id: UUID, **kwargs) -> Expense:
        expense = self.get_expense_or_raise(expense_id)

        for key, value in kwargs.items():
            if hasattr(expense, key):
                setattr(expense, key, value)

        self.expenses[expense_id] = expense
        return expense

    def approve_expense(self, expense_id: UUID, manager_id: str) -> Expense:
        expense = self.get_expense_or_raise(expense_id)

        if expense.status != ExpenseStatus.SUBMITTED:
            raise StateTransitionError(
                f"Can only approve SUBMITTED expenses, current status is {expense.status}"
            )

        expense = self.update_expense(
            expense_id,
            status=ExpenseStatus.MANAGER_APPROVED,
            manager_id=manager_id,
            rejection_reason=None,
        )
        return expense

    def reject_expense(self, expense_id: UUID, manager_id: str, reason: Optional[str] = None) -> Expense:
        expense = self.get_expense_or_raise(expense_id)

        if expense.status != ExpenseStatus.SUBMITTED:
            raise StateTransitionError(
                f"Can only reject SUBMITTED expenses, current status is {expense.status}"
            )

        expense = self.update_expense(
            expense_id,
            status=ExpenseStatus.REJECTED,
            manager_id=manager_id,
            rejection_reason=reason,
        )
        return expense

    def process_expense(self, expense_id: UUID, finance_id: str) -> Expense:
        expense = self.get_expense_or_raise(expense_id)

        if expense.status != ExpenseStatus.MANAGER_APPROVED:
            raise StateTransitionError(
                f"Can only process MANAGER_APPROVED expenses, current status is {expense.status}"
            )

        expense = self.update_expense(
            expense_id,
            status=ExpenseStatus.FINANCE_PROCESSED,
            finance_id=finance_id,
        )
        return expense

    def resubmit_expense(
        self,
        expense_id: UUID,
        amount: float,
        category: str,
        description: str,
        expense_date,
    ) -> Expense:
        expense = self.get_expense_or_raise(expense_id)

        if expense.status != ExpenseStatus.REJECTED:
            raise StateTransitionError(
                f"Can only resubmit REJECTED expenses, current status is {expense.status}"
            )

        expense = self.update_expense(
            expense_id,
            amount=amount,
            category=category,
            description=description,
            expense_date=expense_date,
            status=ExpenseStatus.SUBMITTED,
            manager_id=None,
            rejection_reason=None,
            finance_id=None,
        )
        return expense

    def delete_expense(self, expense_id: UUID) -> None:
        expense = self.get_expense_or_raise(expense_id)

        if expense.status not in [ExpenseStatus.SUBMITTED, ExpenseStatus.REJECTED]:
            raise StateTransitionError(
                f"Can only delete SUBMITTED or REJECTED expenses, current status is {expense.status}"
            )

        del self.expenses[expense_id]

    def create_audit_log(
        self,
        expense_id: UUID,
        action: AuditAction,
        actor_id: str,
        previous_state: Optional[dict] = None,
        new_state: Optional[dict] = None,
        reason: Optional[str] = None,
    ) -> AuditLog:
        audit_id = uuid4()
        audit_log = AuditLog(
            id=audit_id,
            expense_id=expense_id,
            action=action,
            actor_id=actor_id,
            timestamp=datetime.utcnow(),
            previous_state=previous_state,
            new_state=new_state,
            reason=reason,
        )
        self.audit_logs[audit_id] = audit_log
        return audit_log

    def get_audit_logs(self) -> List[AuditLog]:
        return list(self.audit_logs.values())

    def get_audit_logs_by_expense(self, expense_id: UUID) -> List[AuditLog]:
        return [log for log in self.audit_logs.values() if log.expense_id == expense_id]

    def get_audit_logs_by_actor(self, actor_id: str) -> List[AuditLog]:
        return [log for log in self.audit_logs.values() if log.actor_id == actor_id]

    def get_audit_logs_by_action(self, action: AuditAction) -> List[AuditLog]:
        return [log for log in self.audit_logs.values() if log.action == action]
