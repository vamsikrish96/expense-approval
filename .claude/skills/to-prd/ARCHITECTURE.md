# Expense Approval Workflow API - Architecture Design

## Overview
A FastAPI-based REST API for managing employee expense claims with a linear approval workflow: Employee → Manager → Finance. All decisions made with production-quality code in mind.

---

## 1. Approval Workflow

**Flow**: SUBMITTED → MANAGER_APPROVED → FINANCE_PROCESSED (success terminal state)

**Rejection Path**: Any stage can REJECT → claim becomes resubmittable (can edit and resubmit)

**Key Rules**:
- Employees can only view their own claims
- Managers and Finance can view all claims
- Users cannot approve/reject their own claims

---

## 2. Authentication & Authorization

**Method**: Mocked Entra ID JWT with Bearer tokens

**Token Structure** (Fake JWT that mimics Entra ID):
```json
{
  "oid": "user-object-id",
  "preferred_username": "user@company.com",
  "name": "User Name",
  "roles": ["employee|manager|finance"]
}
```

**Authorization Model**:
- **Employee**: Can submit, view own claims, resubmit rejected claims
- **Manager**: Can view all claims, approve/reject
- **Finance**: Can view all claims, process approved claims
- No user can approve/reject their own claim

**Implementation**: Custom middleware extracts token claims and injects authenticated user into request context.

---

## 3. Data Model

### Expense Claim
```python
{
  "id": "UUID",
  "employee_id": "string",
  "amount": "decimal (0 < amount ≤ 100,000)",
  "category": "enum (TRAVEL | MEALS | SUPPLIES | OTHER)",
  "description": "string (10-500 chars, required)",
  "expense_date": "date (past, ≤90 days old)",
  "submitted_at": "ISO 8601 timestamp",
  "status": "enum (SUBMITTED | MANAGER_APPROVED | FINANCE_PROCESSED | REJECTED)",
  "manager_id": "string | null (who approved/rejected)",
  "finance_id": "string | null (who processed)",
  "rejection_reason": "string | null (if REJECTED)"
}
```

### Audit Log Entry
```python
{
  "id": "UUID",
  "expense_id": "UUID",
  "action": "enum (SUBMITTED | APPROVED | REJECTED | RESUBMITTED | PROCESSED | DELETED)",
  "actor_id": "string",
  "timestamp": "ISO 8601",
  "previous_state": "dict (complete expense state before)",
  "new_state": "dict (complete expense state after)",
  "reason": "string | null (rejection reason, if applicable)"
}
```

---

## 4. API Endpoints

### Expense Management
| Method | Endpoint | Role | Action |
|--------|----------|------|--------|
| POST | `/expenses` | Employee | Submit claim |
| GET | `/expenses` | All | List claims (filtered by auth) |
| GET | `/expenses/{id}` | All | View single claim |
| PATCH | `/expenses/{id}/approve` | Manager | Approve claim |
| PATCH | `/expenses/{id}/reject` | Manager/Finance | Reject with reason |
| PATCH | `/expenses/{id}/process` | Finance | Mark as processed |
| PATCH | `/expenses/{id}/resubmit` | Employee | Resubmit rejected claim |
| DELETE | `/expenses/{id}` | Employee | Delete (only SUBMITTED/REJECTED) |

### Audit Logging
| Method | Endpoint | Role | Action |
|--------|----------|------|--------|
| GET | `/audit-logs` | All | List all audit events (optional filters) |
| GET | `/expenses/{id}/audit-log` | All | Full history of single claim |

---

## 5. In-Memory Storage

**Architecture**: Single `InMemoryDatabase` class manages all data

```python
class InMemoryDatabase:
    def __init__(self):
        self.expenses: dict[str, Expense] = {}
        self.audit_logs: dict[str, AuditLog] = {}
        self.users: dict[str, User] = {}  # for role lookup if needed
    
    # Methods for CRUD operations with built-in validation
```

**Design Decisions**:
- No indexes for now (simple O(n) linear scans)
- Can be swapped for real DB later without changing service layer
- All business logic happens in repository layer

**Data Persistence**: In-memory only (resets on app restart). Suitable for demo/testing.

---

## 6. Validation Rules

**Amount**:
- Must be > 0
- Must be ≤ 100,000

**Category**: 
- Enum: TRAVEL, MEALS, SUPPLIES, OTHER
- Required

**Description**:
- Required
- Min 10 characters, Max 500 characters

**Expense Date**:
- Must be in the past (not future)
- Must be within last 90 days
- Required

**Workflow Constraints**:
- Cannot approve/reject your own claim
- Can only resubmit if currently REJECTED
- Can only delete if SUBMITTED or REJECTED (not in approval chain)

---

## 7. Error Handling

**Custom Error Response Format**:
```json
{
  "error": "ERROR_CODE",
  "message": "Human-readable error message",
  "status_code": 400
}
```

**Error Codes** (configurable, centralized):
- `INVALID_AMOUNT` (400)
- `INVALID_CATEGORY` (400)
- `INVALID_DESCRIPTION` (400)
- `INVALID_EXPENSE_DATE` (400)
- `CLAIM_NOT_FOUND` (404)
- `UNAUTHORIZED` (403)
- `INVALID_STATE_TRANSITION` (409)
- `SELF_APPROVAL_NOT_ALLOWED` (409)
- `CLAIM_ALREADY_PROCESSED` (409)
- etc.

**Implementation**: 
- Centralized error definitions (enum or config file)
- Custom exception classes with error codes
- Global exception handler in FastAPI

---

## 8. Testing Strategy

### Unit Tests
- Input validation (amount, category, description, date)
- Business rule enforcement (no self-approval, state transitions)
- Authorization checks (employee can't see other's claims)

### Integration Tests
- Full workflows: submit → approve → process
- Rejection and resubmission flow
- Audit log creation and accuracy
- Role-based access control

### Test Infrastructure
- Pytest with fixtures
- Fresh in-memory DB per test (no pollution)
- Mocked Entra ID tokens for auth testing

---

## 9. Code Organization

```
project/
├── main.py                 # FastAPI app entry point
├── config.py               # Configuration, error codes
├── models/
│   ├── __init__.py
│   ├── expense.py          # Expense domain model
│   ├── audit.py            # AuditLog model
│   └── user.py             # User/auth model
├── database/
│   ├── __init__.py
│   └── memory.py           # InMemoryDatabase class
├── services/
│   ├── __init__.py
│   ├── expense_service.py  # Business logic
│   └── auth_service.py     # Token parsing, user extraction
├── api/
│   ├── __init__.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── expenses.py     # Expense endpoints
│   │   └── audit.py        # Audit log endpoints
│   ├── middleware.py       # Auth middleware
│   └── exceptions.py       # Custom exceptions
├── tests/
│   ├── __init__.py
│   ├── conftest.py         # Pytest fixtures
│   ├── test_models.py
│   ├── test_validation.py
│   ├── test_workflows.py   # Integration tests
│   ├── test_auth.py
│   └── test_api.py
└── requirements.txt
```

---

## 10. Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Linear approval flow | Simple to test, common in enterprises, extensible |
| Resubmittable rejections | More realistic, improves UX |
| Single DB class | Encapsulation, easier to swap for real DB later |
| No indexes initially | Keep simple, add later if needed |
| Mocked Entra ID | Easier to test locally, no external dependencies |
| Custom error codes | Better for frontend handling, centralized management |
| Both unit + integration tests | Comprehensive coverage, both logic and workflow |
| In-memory storage | Suitable for demo, clear upgrade path to persistence |

---

## 11. Future Enhancements

- Real Entra ID integration
- Database persistence (PostgreSQL, MongoDB, etc.)
- Query optimization with indexes
- Bulk approval endpoint
- Expense analytics/reporting
- Email notifications on state changes
- Multi-level manager approval (chain of command)
- Conditional approval thresholds (amount-based routing)

---

## Production Readiness Checklist

- ✅ Input validation on all fields
- ✅ Authentication/Authorization layer
- ✅ Comprehensive error handling
- ✅ Unit + integration tests
- ✅ Audit logging for compliance
- ✅ Clean code organization
- ✅ No unprotected endpoints
- ✅ Configurable error messages
- ✅ State machine validation
- ⏳ Deployment config (Docker, environment vars)
