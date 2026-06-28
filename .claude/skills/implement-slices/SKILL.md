# /implement-slices

Implement feature slices with testing, progress tracking, and git commits.

## Purpose

After publishing feature slices with `/publish-issues`, use this skill to:
1. Run tests for each feature slice
2. Track progress in PROGRESS.md
3. Commit changes to GitHub after successful tests
4. Update task list automatically
5. Respect blocking dependencies between slices

This skill implements the full workflow for slice-based development.

## Usage

```
/implement-slices
```

When invoked, the skill will:
1. Install requirements.txt
2. For each feature slice (in order):
   - Create/update task in task list
   - Run corresponding tests
   - Update PROGRESS.md with results
   - If tests pass: commit to GitHub
   - Mark task as completed
3. Generate final summary

## How It Works

### Step-by-Step Process

For each feature slice:

```
1. Check dependencies (blocked_by)
   ↓
2. Install requirements.txt (first slice only)
   ↓
3. Create task in task list
   ↓
4. Mark task as in_progress
   ↓
5. Run corresponding tests
   ↓
6. Update PROGRESS.md with results
   ↓
7. If tests pass:
   - Create git commit
   - Push to GitHub (optional)
   - Mark task as completed
8. If tests fail:
   - Log error to PROGRESS.md
   - Mark task as blocked
   - Continue to next unblocked slice
```

### Test Execution

For each slice, the skill:
- Identifies corresponding test file(s)
- Installs requirements.txt (if not already installed)
- Runs: `pytest tests/ -v`
- Parses test output
- Records pass/fail counts
- Updates PROGRESS.md

### Git Commit Format

After successful tests:
```
Commit: Implement [Slice N] Title

Body includes:
- Slice number and description
- Test results (X/Y passed)
- Commit hash for tracking
```

## Output: PROGRESS.md

The skill creates/updates PROGRESS.md:

```markdown
# Implementation Progress

**Last Updated**: 2026-06-28T20:30:00Z

## Summary

- Total Slices: 12
- Completed: 3
- In Progress: 1
- Pending: 8
- Failed: 0

## Status by Slice

### ✅ [Slice 1] Foundation: Project Setup & Auth Middleware

- **Status**: completed
- **Tests**: Passed (8/8)
- **Committed**: 2026-06-28T20:05:00Z
- **Commit**: a1b2c3d

### 🔄 [Slice 2] Domain Models & Validation

- **Status**: in_progress
- **Tests**: Running...

### ⏳ [Slice 3] In-Memory Database Layer

- **Status**: pending
- **Blocked by**: Slice 2
```

## Task List Integration

For each slice, the skill:
- Creates task: `{slice_number}. {slice_title}`
- Status: pending → in_progress → completed
- Updates as it progresses
- Provides real-time feedback

Example:
```
#1 [in_progress] [Slice 1] Foundation: Project Setup & Auth
#2 [pending] [Slice 2] Domain Models & Validation
#3 [pending] [Slice 3] In-Memory Database Layer
```

## Slice Dependencies

Slices are implemented in order, respecting blocking relationships:

```
Slice 1 (no blocker)
   ↓
Slice 2 (blocked by Slice 1)
   ↓
Slice 3 (blocked by Slice 2)
   ↓
Slice 4 (blocked by Slice 1)
   ↓
...
```

If a slice's blocker fails, that slice is skipped.

## Requirements

- Python 3.9+
- pytest
- git
- requirements.txt with all dependencies
- Working directory: project root

## Slice-to-Test Mapping

Default mapping for Expense Approval API:

| Slice | Tests |
|-------|-------|
| 1: Auth Middleware | test_auth.py (8 tests) |
| 2: Models | test_models.py (8 tests) |
| 3: Database | test_workflows.py (database subset) |
| 4: Error Handling | error-related tests |
| 5: Submit Expense | test_submit_expense_workflow |
| 6: Approve/Reject | test_manager_approve/reject |
| 7: Process | test_finance_process_expense |
| 8: Resubmit | test_resubmit_rejected_expense |
| 9: List/View | test_list_expenses_role_based_filtering |
| 10: Delete | test_delete_submitted_expense |
| 11: Audit Log | test_audit_log_created |
| 12: E2E & Docs | All tests (full suite) |

## Features

✓ **Sequential processing** - One slice at a time in order
✓ **Dependency respect** - Skips blocked slices
✓ **Test automation** - Runs relevant tests per slice
✓ **Progress tracking** - PROGRESS.md updated in real-time
✓ **Git integration** - Commits on successful tests
✓ **Task list sync** - Updates Claude Code tasks
✓ **Error reporting** - Logs failures clearly
✓ **Requirements check** - Ensures dependencies installed

## Example Execution

Input: 12 feature slices

```
[1/12] [Slice 1] Foundation: Project Setup & Auth Middleware
  → Installing requirements...
  ✓ requirements.txt installed
  → Running tests...
  ✓ 8/8 tests passed
  → Committing...
  ✓ Committed (a1b2c3d)
  → Marking task as completed

[2/12] [Slice 2] Domain Models & Validation
  → Running tests...
  ✓ 8/8 tests passed
  → Committing...
  ✓ Committed (b2c3d4e)
  → Marking task as completed

[3/12] [Slice 3] In-Memory Database Layer
  → Running tests...
  ✓ 3/3 tests passed
  → Committing...
  ✓ Committed (c3d4e5f)
  → Marking task as completed

...

============================================================
Summary: 12/12 slices completed successfully
============================================================
```

## Notes

- Runs locally (no external dependencies)
- Uses native Claude Code tools (Bash, TaskCreate, Write)
- Commits to current branch
- PROGRESS.md always shows current state
- All operations logged and tracked
- Safe to interrupt and resume
