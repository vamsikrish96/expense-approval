# /implement-slices Skill

Automate implementation of feature slices with testing, progress tracking, and git commits.

## Overview

This skill provides end-to-end automation for implementing feature slices:

1. **Sequential Implementation** - Processes slices in order, respecting dependencies
2. **Automated Testing** - Runs relevant tests for each slice
3. **Progress Tracking** - Updates PROGRESS.md for visibility
4. **Git Integration** - Commits changes after successful tests
5. **Task Management** - Updates Claude Code task list

## Workflow

```
/publish-issues
       ↓
/implement-slices
       ↓
PROGRESS.md (updated)
       ↓
GitHub (commits created)
       ↓
Task List (updated)
```

## Quick Start

### Basic Usage

```bash
/implement-slices --repo vamsikrish96/expense-approval
```

### With Options

```bash
/implement-slices \
  --repo vamsikrish96/expense-approval \
  --progress-file PROGRESS.md \
  --skip-tests
```

## Process for Each Slice

```
1. Check if blocked by other slices
   ↓
2. Install requirements.txt
   ↓
3. Run corresponding unit tests
   ↓
4. If tests pass:
   - Create git commit
   - Update PROGRESS.md
   - Mark task as completed
5. If tests fail:
   - Log error to PROGRESS.md
   - Mark task as blocked
   - Continue to next slice
```

## Configuration

### Slice-to-Test Mapping

The skill automatically maps slices to test files. For the Expense Approval API:

| Slice | Tests |
|-------|-------|
| 1: Auth | test_auth.py (8 tests) |
| 2: Models | test_models.py (8 tests) |
| 3: Database | test_workflows.py (subset) |
| 4: Error Handling | All error-related tests |
| 5: Submit | test_submit_expense_workflow |
| 6: Approve/Reject | test_manager_approve/reject |
| 7: Process | test_finance_process_expense |
| 8: Resubmit | test_resubmit_rejected_expense |
| 9: List/View | test_list_expenses_role_based_filtering |
| 10: Delete | test_delete_submitted_expense |
| 11: Audit | test_audit_log_created |
| 12: E2E | All tests (full suite) |

### Custom Test Mapping

Create a JSON file to map slices to tests:

```json
{
  "Slice 1": {
    "test_file": "tests/test_auth.py"
  },
  "Slice 2": {
    "test_file": "tests/test_models.py"
  },
  "Slice 3": {
    "test_file": "tests/test_workflows.py",
    "test_pattern": "database"
  }
}
```

Then use:
```bash
/implement-slices --repo myorg/myapp --test-map mapping.json
```

## Example Execution

### Input: 12 Feature Slices

```bash
/implement-slices --repo vamsikrish96/expense-approval
```

### Output Progress

```
Implementing feature slices for vamsikrish96/expense-approval...

Installing requirements...
✓ requirements.txt installed

[1/12] [Slice 1] Foundation: Project Setup & Auth Middleware
  → Running tests: test_auth.py...
  ✓ 8 tests passed
  → Committing changes...
  ✓ Committed (a1b2c3d)
  → Marking as completed

[2/12] [Slice 2] Domain Models & Validation
  → Running tests: test_models.py...
  ✓ 8 tests passed
  → Committing changes...
  ✓ Committed (b2c3d4e)
  → Marking as completed

[3/12] [Slice 3] In-Memory Database Layer
  → Running tests: test_workflows.py...
  ✓ 3 tests passed
  → Committing changes...
  ✓ Committed (c3d4e5f)
  → Marking as completed

[4/12] [Slice 4] Error Handling & Configuration
  → Running tests: test_*.py...
  ✓ Tests passed
  → Committing changes...
  ✓ Committed (d4e5f6g)
  → Marking as completed

[5/12] [Slice 5] Employee: Submit Expense Claim
  → Running tests: test_submit_expense_workflow...
  ✓ 1 test passed
  → Committing changes...
  ✓ Committed (e5f6g7h)
  → Marking as completed

...

============================================================
Implementation Summary: 12/12 slices completed
============================================================

Progress saved to PROGRESS.md
```

### PROGRESS.md Generated

```markdown
# Implementation Progress

**Last Updated**: 2026-06-28T20:30:00Z

## Summary

- Total Slices: 12
- Completed: 12
- In Progress: 0
- Pending: 0
- Failed: 0

## Status by Slice

### ✅ [Slice 1] Foundation: Project Setup & Auth Middleware

- **Status**: completed
- **Tests**: Passed (8/8)
- **Committed**: 2026-06-28T20:05:00Z
- **Commit**: a1b2c3d

### ✅ [Slice 2] Domain Models & Validation

- **Status**: completed
- **Tests**: Passed (8/8)
- **Committed**: 2026-06-28T20:10:00Z
- **Commit**: b2c3d4e

...
```

### Git Commits Created

```
commit a1b2c3d
Author: Claude Haiku 4.5 <noreply@anthropic.com>

    Implement [Slice 1] Foundation: Project Setup & Auth Middleware

    Slice #1: Set up FastAPI with mocked Entra ID JWT auth

    Tests: 8/8 passed

    Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>

commit b2c3d4e
Author: Claude Haiku 4.5 <noreply@anthropic.com>

    Implement [Slice 2] Domain Models & Validation

    Slice #2: Create Pydantic models with validation

    Tests: 8/8 passed
```

## Options in Detail

### --repo (Required)
GitHub repository in format `owner/repo`

### --progress-file
Path to progress tracking file (default: PROGRESS.md)

### --skip-tests
Skip running tests for each slice (useful for demonstration)

### --no-commit
Don't create git commits after successful tests

### --parallel
Run multiple slices in parallel (default: sequential)

### --max-parallel
Maximum number of parallel slices (default: 3)

### --only-failed
Only implement slices that previously failed

## Task List Integration

The skill automatically:
- Creates a task for each slice
- Marks as `in_progress` when implementing
- Marks as `completed` when tests pass
- Marks as `blocked` if tests fail

Tasks can be viewed with `/help` or in the task list.

## Error Handling

### Test Failures

If a test fails:
1. Error logged to PROGRESS.md
2. Slice marked as "failed"
3. Implementation continues to next slice
4. User can review failures and retry

### Git Commit Failures

If git commit fails:
1. Tests still passed ✓
2. Changes are staged
3. Manual commit may be needed
4. Logged to PROGRESS.md

### Requirements Installation Failures

If requirements.txt installation fails:
1. Process stops
2. User must install manually
3. Re-run skill after manual fix

## Advanced Features

### Dry-Run Mode

```bash
/implement-slices --repo myorg/myapp --dry-run
```

Preview what would happen without making changes.

### Retry Failed Slices

```bash
/implement-slices --repo myorg/myapp --retry-failed
```

Re-implement only slices marked as failed.

### Custom Commit Messages

```bash
/implement-slices --repo myorg/myapp \
  --commit-template "Implement {slice_title}\n\nCloses #{issue_number}"
```

### Post-Implementation Hooks

```bash
/implement-slices --repo myorg/myapp \
  --on-success "npm run build" \
  --on-failure "npm run lint"
```

Run commands after each slice (success or failure).

## Best Practices

### Before Running

1. **Ensure clean git state**: `git status` should show no uncommitted changes
2. **Update requirements.txt** if dependencies changed
3. **Review PROGRESS.md** to understand current state
4. **Have tests ready** for each slice

### During Execution

1. **Monitor progress** in real-time
2. **Check PROGRESS.md** for failures
3. **Review commits** in GitHub

### After Execution

1. **Verify all tests passed**
2. **Check PROGRESS.md** for summary
3. **Review git log** for commits
4. **Push to GitHub** (if not auto-pushed)

## Troubleshooting

### "Tests failed for Slice X"

Check PROGRESS.md for error details:
```bash
cat PROGRESS.md | grep -A5 "Slice X"
```

Run tests manually:
```bash
pytest tests/ -v
```

### "Requirements not installed"

Install manually:
```bash
pip install -r requirements.txt
```

Then re-run skill.

### "Git commit failed"

Check git status:
```bash
git status
```

Resolve conflicts/issues, then re-run.

### "No tests found for Slice X"

Verify test file exists:
```bash
ls tests/test_*.py
```

Update test mapping or create tests.

## Integration with CI/CD

This skill can be integrated with CI/CD pipelines:

```bash
# GitHub Actions example
- name: Implement Slices
  run: /implement-slices --repo ${{ github.repository }}
```

Or with other tools:
- Jenkins
- GitLab CI
- CircleCI
- Travis CI

## Environment

The skill requires:
- Python 3.9+
- pytest
- git
- requirements.txt with all dependencies

## Notes

- Implementation requires write access to repository
- Tests must be properly organized in tests/ directory
- One slice at a time (sequential by default)
- Task list updates require Claude Code context
- PROGRESS.md is created automatically
