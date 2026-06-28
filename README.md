# Expense Approval Workflow API

A production-quality FastAPI application for managing employee expense claims with a linear approval workflow. Employees submit expense claims, managers review and approve or reject them, and finance processes approved claims.

## Features

- **Employee-initiated workflow**: Employees submit expense claims with automatic validation
- **Manager approval**: Managers can approve or reject claims with optional reasons
- **Finance processing**: Finance team processes approved claims
- **Rejection & resubmission**: Employees can edit and resubmit rejected claims
- **Audit logging**: Complete audit trail for compliance tracking
- **Role-based access control**: Different views and permissions for employees, managers, and finance
- **Mocked Entra ID authentication**: JWT-based auth ready for real Entra ID integration
- **Input validation**: Strict business rules enforcement (amount limits, date constraints, etc.)
- **Production-ready code**: Comprehensive tests, error handling, and code organization

## Architecture

### Approval Workflow

```
SUBMITTED → MANAGER_APPROVED → FINANCE_PROCESSED (success)
    ↓
REJECTED (terminal, but can resubmit)
```

### Tech Stack

- **Framework**: FastAPI 0.104.1
- **Server**: Uvicorn
- **Data validation**: Pydantic 2.5.0
- **Testing**: Pytest 7.4.3
- **Authentication**: Mocked JWT (ready for Entra ID)
- **Storage**: In-memory (demo/testing)

### Project Structure

```
expense-approval/
├── models/                 # Domain models
│   ├── expense.py         # Expense and validation
│   ├── audit.py           # Audit log model
│   └── user.py            # User and roles
├── database/              # Data persistence
│   └── memory.py          # In-memory database
├── services/              # Business logic
│   ├── expense_service.py # Workflow operations
│   └── auth_service.py    # JWT handling
├── api/                   # API layer
│   ├── routes/
│   │   ├── expenses.py    # Expense endpoints
│   │   └── audit.py       # Audit log endpoints
│   ├── exceptions.py      # Custom exceptions
│   └── middleware.py      # Auth middleware
├── tests/                 # Test suite
│   ├── conftest.py        # Pytest fixtures
│   ├── test_auth.py       # Auth tests
│   ├── test_models.py     # Model validation tests
│   └── test_workflows.py  # Integration tests
├── config.py              # Configuration & error codes
├── main.py                # FastAPI app entry point
└── requirements.txt       # Dependencies
```

## Setup

### Prerequisites

- Python 3.9+
- pip/conda

### Installation

1. Clone the repository
```bash
git clone https://github.com/vamsikrish96/expense-approval.git
cd expense-approval
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Run the API
```bash
python main.py
```

The API will start on `http://localhost:8000`

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_workflows.py -v

# Run with coverage
pytest tests/ --cov=.
```

Test coverage: **25/25 tests passing** ✓

## API Documentation

### Interactive Docs

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Authentication

All endpoints require a Bearer token in the `Authorization` header:

```
Authorization: Bearer <JWT_TOKEN>
```

#### Sample JWT Tokens

You can generate fake JWT tokens using the `create_fake_jwt_token` function:

```python
from services.auth_service import create_fake_jwt_token

# Employee token
employee_token = create_fake_jwt_token(
    oid="emp-001",
    preferred_username="john.doe@company.com",
    name="John Doe",
    roles=["employee"]
)

# Manager token
manager_token = create_fake_jwt_token(
    oid="mgr-001",
    preferred_username="jane.smith@company.com",
    name="Jane Smith",
    roles=["manager"]
)

# Finance token
finance_token = create_fake_jwt_token(
    oid="fin-001",
    preferred_username="bob.wilson@company.com",
    name="Bob Wilson",
    roles=["finance"]
)
```

### Endpoints

#### 1. Submit Expense Claim

**Endpoint**: `POST /expenses`

**Required role**: Employee

**Request body**:
```json
{
  "amount": 500.00,
  "category": "TRAVEL",
  "description": "Conference attendance in New York",
  "expense_date": "2026-06-23"
}
```

**Response** (201 Created):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "employee_id": "emp-001",
  "amount": 500.00,
  "category": "TRAVEL",
  "description": "Conference attendance in New York",
  "expense_date": "2026-06-23",
  "submitted_at": "2026-06-28T15:30:00",
  "status": "SUBMITTED",
  "manager_id": null,
  "finance_id": null,
  "rejection_reason": null
}
```

**Example cURL**:
```bash
curl -X POST "http://localhost:8000/expenses" \
  -H "Authorization: Bearer $EMPLOYEE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 500,
    "category": "TRAVEL",
    "description": "Conference attendance in New York",
    "expense_date": "2026-06-23"
  }'
```

#### 2. List Expenses

**Endpoint**: `GET /expenses`

**Access**:
- Employees see only their own expenses
- Managers see all expenses
- Finance see all expenses

**Example cURL**:
```bash
curl -X GET "http://localhost:8000/expenses" \
  -H "Authorization: Bearer $TOKEN"
```

#### 3. Get Expense Detail

**Endpoint**: `GET /expenses/{expense_id}`

**Access**: Owner or manager/finance

**Example**:
```bash
curl -X GET "http://localhost:8000/expenses/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer $TOKEN"
```

#### 4. Manager: Approve Expense

**Endpoint**: `PATCH /expenses/{expense_id}/approve`

**Required role**: Manager

**Response** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "MANAGER_APPROVED",
  "manager_id": "mgr-001",
  ...
}
```

**Example cURL**:
```bash
curl -X PATCH "http://localhost:8000/expenses/550e8400-e29b-41d4-a716-446655440000/approve" \
  -H "Authorization: Bearer $MANAGER_TOKEN"
```

#### 5. Manager: Reject Expense

**Endpoint**: `PATCH /expenses/{expense_id}/reject`

**Required role**: Manager

**Query parameter**: `reason` (optional)

**Example cURL**:
```bash
curl -X PATCH "http://localhost:8000/expenses/550e8400-e29b-41d4-a716-446655440000/reject?reason=Missing receipt" \
  -H "Authorization: Bearer $MANAGER_TOKEN"
```

#### 6. Finance: Process Expense

**Endpoint**: `PATCH /expenses/{expense_id}/process`

**Required role**: Finance

**Note**: Can only process MANAGER_APPROVED expenses

**Example cURL**:
```bash
curl -X PATCH "http://localhost:8000/expenses/550e8400-e29b-41d4-a716-446655440000/process" \
  -H "Authorization: Bearer $FINANCE_TOKEN"
```

#### 7. Employee: Resubmit Rejected Claim

**Endpoint**: `PATCH /expenses/{expense_id}/resubmit`

**Required role**: Employee (owner)

**Request body**: Updated expense data (same as submit)

**Note**: Can only resubmit REJECTED expenses

**Example cURL**:
```bash
curl -X PATCH "http://localhost:8000/expenses/550e8400-e29b-41d4-a716-446655440000/resubmit" \
  -H "Authorization: Bearer $EMPLOYEE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 450.00,
    "category": "TRAVEL",
    "description": "Conference attendance with receipt attached",
    "expense_date": "2026-06-23"
  }'
```

#### 8. Employee: Delete Claim

**Endpoint**: `DELETE /expenses/{expense_id}`

**Required role**: Employee (owner)

**Note**: Can only delete SUBMITTED or REJECTED expenses

**Response**: 204 No Content

**Example cURL**:
```bash
curl -X DELETE "http://localhost:8000/expenses/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer $EMPLOYEE_TOKEN"
```

#### 9. Get Audit Logs

**Endpoint**: `GET /audit-logs`

**Access**: All authenticated users

**Response** (200 OK):
```json
[
  {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "expense_id": "550e8400-e29b-41d4-a716-446655440000",
    "action": "SUBMITTED",
    "actor_id": "emp-001",
    "timestamp": "2026-06-28T15:30:00",
    "previous_state": null,
    "new_state": { "id": "...", "status": "SUBMITTED", ... },
    "reason": null
  },
  {
    "id": "660e8400-e29b-41d4-a716-446655440002",
    "expense_id": "550e8400-e29b-41d4-a716-446655440000",
    "action": "APPROVED",
    "actor_id": "mgr-001",
    "timestamp": "2026-06-28T15:45:00",
    "previous_state": { "status": "SUBMITTED", ... },
    "new_state": { "status": "MANAGER_APPROVED", ... },
    "reason": null
  }
]
```

#### 10. Get Expense Audit Trail

**Endpoint**: `GET /audit-logs/{expense_id}/detail`

**Access**: Owner or manager/finance

**Returns**: All audit events for a specific expense

**Example**:
```bash
curl -X GET "http://localhost:8000/audit-logs/550e8400-e29b-41d4-a716-446655440000/detail" \
  -H "Authorization: Bearer $TOKEN"
```

## Validation Rules

### Amount
- **Range**: Greater than 0, less than or equal to 100,000
- **Error**: Returns 400 if outside range

### Category
- **Valid values**: `TRAVEL`, `MEALS`, `SUPPLIES`, `OTHER`
- **Error**: Returns 400 if invalid

### Description
- **Length**: 10-500 characters
- **Required**: Yes
- **Error**: Returns 400 if invalid

### Expense Date
- **Constraint**: Must be in the past
- **Age limit**: Not older than 90 days
- **Error**: Returns 400 if invalid

## Workflow Example

### Full Workflow: Submit → Approve → Process

```bash
#!/bin/bash

# 1. Employee submits expense
EXPENSE_ID=$(curl -s -X POST "http://localhost:8000/expenses" \
  -H "Authorization: Bearer $EMPLOYEE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 500,
    "category": "TRAVEL",
    "description": "Conference attendance in New York",
    "expense_date": "2026-06-23"
  }' | jq -r '.id')

echo "Submitted expense: $EXPENSE_ID"

# 2. Manager approves
curl -s -X PATCH "http://localhost:8000/expenses/$EXPENSE_ID/approve" \
  -H "Authorization: Bearer $MANAGER_TOKEN" | jq '.status'

# 3. Finance processes
curl -s -X PATCH "http://localhost:8000/expenses/$EXPENSE_ID/process" \
  -H "Authorization: Bearer $FINANCE_TOKEN" | jq '.status'

# 4. View audit trail
curl -s -X GET "http://localhost:8000/audit-logs/$EXPENSE_ID/detail" \
  -H "Authorization: Bearer $EMPLOYEE_TOKEN" | jq 'length'
```

## Error Codes

| Code | Status | Description |
|------|--------|-------------|
| INVALID_AMOUNT | 400 | Amount outside valid range |
| INVALID_CATEGORY | 400 | Invalid expense category |
| INVALID_DESCRIPTION | 400 | Description length invalid |
| INVALID_EXPENSE_DATE | 400 | Date in future or too old |
| CLAIM_NOT_FOUND | 404 | Expense not found |
| UNAUTHORIZED | 401 | Missing or invalid token |
| FORBIDDEN | 403 | Insufficient permissions |
| INVALID_STATE_TRANSITION | 409 | Invalid workflow state change |
| SELF_APPROVAL_NOT_ALLOWED | 409 | Cannot approve own expense |

## Security Considerations

- **Authentication**: All endpoints require valid JWT token
- **Authorization**: Role-based access control enforced
- **Audit logging**: All actions are logged with actor information
- **Input validation**: All inputs validated before processing
- **Error handling**: Consistent error responses without information leakage

### Future Enhancements

- Real Entra ID integration
- Database persistence (PostgreSQL, MongoDB)
- Encrypted audit logs
- Email notifications on state changes
- Expense analytics and reporting
- Multi-level manager approval chains
- Amount-based routing (conditional approvals)

## Development

### Adding New Features

1. Define models in `models/`
2. Implement business logic in `services/`
3. Create API endpoints in `api/routes/`
4. Add tests in `tests/`
5. Update documentation

### Testing

```bash
# Run all tests with verbose output
pytest tests/ -v

# Run specific test
pytest tests/test_workflows.py::test_submit_expense_workflow -v

# Run with coverage report
pytest tests/ --cov=. --cov-report=html
```

## License

This project is provided as-is for educational and demonstration purposes.

## Support

For issues, questions, or feedback, please create a GitHub issue in the repository.
