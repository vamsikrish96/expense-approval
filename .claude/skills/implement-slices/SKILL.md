# /implement-slices

Implement feature slices and track progress with testing and commits.

## Purpose

After publishing feature slices with `/publish-issues`, use this skill to:
- Implement each feature slice
- Run corresponding unit tests
- Track progress in PROGRESS.md
- Commit changes to GitHub with detailed messages
- Update task list automatically

This skill automates the development workflow for vertical slices.

## Usage

```bash
/implement-slices [options]
```

## Options

```
--repo OWNER/REPO          GitHub repository (required)
--slices slice1,slice2     Specific slices to implement (optional, defaults to all)
--skip-tests               Skip running tests for each slice
--no-commit                Don't commit changes after each slice
--progress-file FILE       Path to progress file (default: PROGRESS.md)
--parallel                 Run slices in parallel (default: sequential)
```

## Workflow

```
For each feature slice:
  1. Read issue/slice details
  2. Create task in task list
  3. Mark task as in_progress
  4. Install requirements.txt
  5. Run relevant unit tests
  6. Update PROGRESS.md
  7. If tests pass:
     - Create git commit with details
     - Mark task as completed
  8. If tests fail:
     - Log error to PROGRESS.md
     - Mark task as blocked
```

## Output

### PROGRESS.md Format

```markdown
# Implementation Progress

**Last Updated**: 2026-06-28T20:15:00Z

## Summary

- Total Slices: 12
- Completed: 3
- In Progress: 1
- Pending: 8
- Failed: 0

## Status by Slice

### ✅ [Slice 1] Foundation: Project Setup & Auth Middleware

- **Status**: Completed
- **Tests**: Passed (8/8)
- **Committed**: 2026-06-28 20:05:00
- **Commit**: a1b2c3d4

### ✅ [Slice 2] Domain Models & Validation

- **Status**: Completed
- **Tests**: Passed (8/8)
- **Committed**: 2026-06-28 20:10:00
- **Commit**: b2c3d4e5

### 🔄 [Slice 3] In-Memory Database Layer

- **Status**: In Progress
- **Tests**: Running...

### ⏳ [Slice 4] Error Handling & Configuration

- **Status**: Pending
- **Tests**: Not run yet
```

## Example

### Command

```bash
/implement-slices --repo vamsikrish96/expense-approval --progress-file PROGRESS.md
```

### Output

```
Implementing feature slices for vamsikrish96/expense-approval...

Installing requirements...
✓ requirements.txt installed

Processing slices:

[1/12] [Slice 1] Foundation: Project Setup & Auth Middleware
  → Running tests: test_auth.py...
  ✓ 8/8 tests passed
  → Committing changes...
  ✓ Committed (abc1234)
  → Marking task as completed

[2/12] [Slice 2] Domain Models & Validation
  → Running tests: test_models.py...
  ✓ 8/8 tests passed
  → Committing changes...
  ✓ Committed (def5678)
  → Marking task as completed

[3/12] [Slice 3] In-Memory Database Layer
  → Running tests: test_workflows.py (database tests)...
  ✓ 3/3 tests passed
  → Committing changes...
  ✓ Committed (ghi9012)
  → Marking task as completed

Progress saved to PROGRESS.md
```

## Slice-to-Test Mapping

The skill maps slices to test files:

| Slice | Test File | Test Count |
|-------|-----------|-----------|
| Slice 1: Auth | test_auth.py | 8 |
| Slice 2: Models | test_models.py | 8 |
| Slice 3: Database | test_workflows.py | 9 (subset) |
| Slice 4: Error Handling | test_*.py | Mixed |
| Slice 5: Submit | test_workflows.py::test_submit_expense_workflow | 1 |
| Slice 6: Approve/Reject | test_workflows.py (approve/reject tests) | 2 |
| Slice 7: Process | test_workflows.py::test_finance_process_expense | 1 |
| Slice 8: Resubmit | test_workflows.py::test_resubmit_rejected_expense | 1 |
| Slice 9: List/View | test_workflows.py::test_list_expenses_role_based_filtering | 1 |
| Slice 10: Delete | test_workflows.py::test_delete_submitted_expense | 1 |
| Slice 11: Audit | test_workflows.py::test_audit_log_created | 1 |
| Slice 12: E2E & Docs | pytest tests/ | All |

## Features

✓ **Automatic test discovery** - Finds relevant tests for each slice
✓ **Dependency tracking** - Respects blocking relationships
✓ **Progress tracking** - PROGRESS.md keeps stakeholders informed
✓ **Git integration** - Commits after successful tests
✓ **Task management** - Updates Claude Code task list
✓ **Error handling** - Reports failures clearly
✓ **Sequential execution** - Implements slices in order

## Integration Points

### With /publish-issues
```
/publish-issues → Creates GitHub issues
/implement-slices → Implements each issue
```

### With GitHub
- Reads issue/PR details
- Creates feature branches (optional)
- Commits with issue references (#N)
- Updates repository

### With Claude Code
- Creates/updates tasks in task list
- Marks completion
- Provides progress summaries

## Configuration

### Custom Test Mapping

```bash
/implement-slices --repo myorg/myapp \
  --test-map '{
    "Slice 1": "tests/test_auth.py",
    "Slice 2": "tests/test_models.py"
  }'
```

### Skip Specific Slices

```bash
/implement-slices --repo myorg/myapp \
  --skip "Slice 4,Slice 5"
```

### Parallel Implementation

```bash
/implement-slices --repo myorg/myapp \
  --parallel \
  --max-parallel 3
```

## Safety Features

- ✓ **Dry-run mode** - Preview changes without committing
- ✓ **Rollback on failure** - Can revert failed commits
- ✓ **Test gating** - Won't commit unless tests pass
- ✓ **Progress backup** - PROGRESS.md versioned
- ✓ **Manual approval** - Can pause between slices

## Advanced Usage

### Conditional Implementation

```bash
/implement-slices --repo myorg/myapp \
  --only-failed
  --retry-limit 3
```

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

## Troubleshooting

### "Tests failed for Slice X"
- Check test output in PROGRESS.md
- Review recent code changes
- Run tests manually: `pytest tests/ -v`

### "Git commit failed"
- Check git status: `git status`
- Ensure no merge conflicts
- Try manual commit

### "Requirements not installed"
- Check requirements.txt
- Run: `pip install -r requirements.txt`
- Check Python environment

## Notes

- Requires Python, pytest, and git
- Needs GitHub repository access
- Task list updates require Claude Code
- PROGRESS.md automatically created/updated
