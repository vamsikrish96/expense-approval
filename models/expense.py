from enum import Enum
from typing import Optional
from datetime import date, datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, field_validator
import re


class Category(str, Enum):
    TRAVEL = "TRAVEL"
    MEALS = "MEALS"
    SUPPLIES = "SUPPLIES"
    OTHER = "OTHER"


class ExpenseStatus(str, Enum):
    SUBMITTED = "SUBMITTED"
    MANAGER_APPROVED = "MANAGER_APPROVED"
    FINANCE_PROCESSED = "FINANCE_PROCESSED"
    REJECTED = "REJECTED"


class ExpenseCreate(BaseModel):
    amount: float
    category: Category
    description: str
    expense_date: date

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: float) -> float:
        if v <= 0 or v > 100000:
            raise ValueError("Amount must be greater than 0 and less than or equal to 100,000")
        return v

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: Category) -> Category:
        if v not in Category:
            raise ValueError(f"Category must be one of: {', '.join([c.value for c in Category])}")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        if not v or len(v) < 10 or len(v) > 500:
            raise ValueError("Description must be between 10 and 500 characters")
        return v

    @field_validator("expense_date")
    @classmethod
    def validate_expense_date(cls, v: date) -> date:
        today = date.today()
        if v > today:
            raise ValueError("Expense date must be in the past")
        days_diff = (today - v).days
        if days_diff > 90:
            raise ValueError("Expense date must not be older than 90 days")
        return v


class ExpenseUpdate(BaseModel):
    amount: Optional[float] = None
    category: Optional[Category] = None
    description: Optional[str] = None
    expense_date: Optional[date] = None

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and (v <= 0 or v > 100000):
            raise ValueError("Amount must be greater than 0 and less than or equal to 100,000")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and (not v or len(v) < 10 or len(v) > 500):
            raise ValueError("Description must be between 10 and 500 characters")
        return v

    @field_validator("expense_date")
    @classmethod
    def validate_expense_date(cls, v: Optional[date]) -> Optional[date]:
        if v is not None:
            today = date.today()
            if v > today:
                raise ValueError("Expense date must be in the past")
            days_diff = (today - v).days
            if days_diff > 90:
                raise ValueError("Expense date must not be older than 90 days")
        return v


class Expense(BaseModel):
    id: UUID
    employee_id: str
    amount: float
    category: Category
    description: str
    expense_date: date
    submitted_at: datetime
    status: ExpenseStatus
    manager_id: Optional[str] = None
    finance_id: Optional[str] = None
    rejection_reason: Optional[str] = None

    class Config:
        use_enum_values = False
