import pytest
from datetime import date, timedelta
from models import ExpenseCreate, Category


def test_expense_create_valid():
    expense = ExpenseCreate(
        amount=500.00,
        category=Category.TRAVEL,
        description="Conference attendance in New York",
        expense_date=date.today() - timedelta(days=5),
    )
    assert expense.amount == 500.00
    assert expense.category == Category.TRAVEL


def test_expense_create_invalid_amount_zero():
    with pytest.raises(ValueError, match="Amount must be greater than 0"):
        ExpenseCreate(
            amount=0,
            category=Category.TRAVEL,
            description="Conference attendance in New York",
            expense_date=date.today() - timedelta(days=5),
        )


def test_expense_create_invalid_amount_too_high():
    with pytest.raises(ValueError, match="Amount must be greater than 0"):
        ExpenseCreate(
            amount=150000,
            category=Category.TRAVEL,
            description="Conference attendance in New York",
            expense_date=date.today() - timedelta(days=5),
        )


def test_expense_create_invalid_description_too_short():
    with pytest.raises(ValueError, match="Description must be between 10 and 500"):
        ExpenseCreate(
            amount=500,
            category=Category.TRAVEL,
            description="Short",
            expense_date=date.today() - timedelta(days=5),
        )


def test_expense_create_invalid_description_too_long():
    with pytest.raises(ValueError, match="Description must be between 10 and 500"):
        ExpenseCreate(
            amount=500,
            category=Category.TRAVEL,
            description="x" * 501,
            expense_date=date.today() - timedelta(days=5),
        )


def test_expense_create_future_date():
    with pytest.raises(ValueError, match="Expense date must be in the past"):
        ExpenseCreate(
            amount=500,
            category=Category.TRAVEL,
            description="Conference attendance",
            expense_date=date.today() + timedelta(days=1),
        )


def test_expense_create_old_date():
    with pytest.raises(ValueError, match="Expense date must not be older than 90 days"):
        ExpenseCreate(
            amount=500,
            category=Category.TRAVEL,
            description="Conference attendance",
            expense_date=date.today() - timedelta(days=91),
        )


def test_expense_create_all_categories():
    for category in Category:
        expense = ExpenseCreate(
            amount=500,
            category=category,
            description="Valid description",
            expense_date=date.today() - timedelta(days=5),
        )
        assert expense.category == category
