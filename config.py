from enum import Enum
from dataclasses import dataclass


class ErrorCode(str, Enum):
    INVALID_AMOUNT = "INVALID_AMOUNT"
    INVALID_CATEGORY = "INVALID_CATEGORY"
    INVALID_DESCRIPTION = "INVALID_DESCRIPTION"
    INVALID_EXPENSE_DATE = "INVALID_EXPENSE_DATE"
    CLAIM_NOT_FOUND = "CLAIM_NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    INVALID_STATE_TRANSITION = "INVALID_STATE_TRANSITION"
    SELF_APPROVAL_NOT_ALLOWED = "SELF_APPROVAL_NOT_ALLOWED"
    CLAIM_ALREADY_PROCESSED = "CLAIM_ALREADY_PROCESSED"
    INVALID_TOKEN = "INVALID_TOKEN"
    MISSING_TOKEN = "MISSING_TOKEN"


@dataclass
class ErrorMessage:
    code: ErrorCode
    message: str
    status_code: int


ERROR_MESSAGES = {
    ErrorCode.INVALID_AMOUNT: ErrorMessage(
        code=ErrorCode.INVALID_AMOUNT,
        message="Amount must be greater than 0 and less than or equal to 100,000",
        status_code=400,
    ),
    ErrorCode.INVALID_CATEGORY: ErrorMessage(
        code=ErrorCode.INVALID_CATEGORY,
        message="Category must be one of: TRAVEL, MEALS, SUPPLIES, OTHER",
        status_code=400,
    ),
    ErrorCode.INVALID_DESCRIPTION: ErrorMessage(
        code=ErrorCode.INVALID_DESCRIPTION,
        message="Description must be between 10 and 500 characters",
        status_code=400,
    ),
    ErrorCode.INVALID_EXPENSE_DATE: ErrorMessage(
        code=ErrorCode.INVALID_EXPENSE_DATE,
        message="Expense date must be in the past and not older than 90 days",
        status_code=400,
    ),
    ErrorCode.CLAIM_NOT_FOUND: ErrorMessage(
        code=ErrorCode.CLAIM_NOT_FOUND,
        message="Expense claim not found",
        status_code=404,
    ),
    ErrorCode.UNAUTHORIZED: ErrorMessage(
        code=ErrorCode.UNAUTHORIZED,
        message="Unauthorized - valid authentication token required",
        status_code=401,
    ),
    ErrorCode.FORBIDDEN: ErrorMessage(
        code=ErrorCode.FORBIDDEN,
        message="Forbidden - insufficient permissions",
        status_code=403,
    ),
    ErrorCode.INVALID_STATE_TRANSITION: ErrorMessage(
        code=ErrorCode.INVALID_STATE_TRANSITION,
        message="Invalid state transition for expense claim",
        status_code=409,
    ),
    ErrorCode.SELF_APPROVAL_NOT_ALLOWED: ErrorMessage(
        code=ErrorCode.SELF_APPROVAL_NOT_ALLOWED,
        message="Cannot approve or reject your own expense claim",
        status_code=409,
    ),
    ErrorCode.CLAIM_ALREADY_PROCESSED: ErrorMessage(
        code=ErrorCode.CLAIM_ALREADY_PROCESSED,
        message="Expense claim has already been processed",
        status_code=409,
    ),
    ErrorCode.INVALID_TOKEN: ErrorMessage(
        code=ErrorCode.INVALID_TOKEN,
        message="Invalid authentication token",
        status_code=401,
    ),
    ErrorCode.MISSING_TOKEN: ErrorMessage(
        code=ErrorCode.MISSING_TOKEN,
        message="Authentication token is missing",
        status_code=401,
    ),
}
