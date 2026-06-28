# /publish-issues

Create GitHub issues for finalized feature slices.

## Purpose

Once you've finalized your feature slices (e.g., using `/to-issues`), use this skill to automatically create GitHub issues for each slice. The skill handles:

- Creating issues in dependency order (blockers first)
- Linking blocking relationships between issues
- Formatting issue bodies with acceptance criteria
- Adding labels for triage

## Usage

```
/publish-issues owner/repo slice1 slice2 slice3
```

Or with a JSON file:

```
/publish-issues owner/repo --from-file slices.json
```

## Input Format

### Command-line Arguments

```bash
/publish-issues vamsikrish96/expense-approval \
  "[Slice 1] Foundation: Project Setup & Auth Middleware" \
  "[Slice 2] Domain Models & Validation" \
  "[Slice 3] In-Memory Database Layer"
```

### JSON File Format

```json
[
  {
    "title": "[Slice 1] Foundation: Project Setup & Auth Middleware",
    "description": "Set up FastAPI with mocked Entra ID JWT auth...",
    "acceptance_criteria": [
      "FastAPI app initialized",
      "JWT token parser works",
      "Auth middleware extracts claims"
    ],
    "blocked_by": null,
    "labels": ["slice", "foundation"]
  },
  {
    "title": "[Slice 2] Domain Models & Validation",
    "description": "Create Pydantic models...",
    "acceptance_criteria": [...],
    "blocked_by": 1,
    "labels": ["slice", "models"]
  }
]
```

## Output

- GitHub issues created in order (blockers first)
- Links to created issues printed to console
- Issues numbered sequentially
- Blocking relationships established

## Example

### Input (JSON)

```json
[
  {
    "title": "[Slice 1] Foundation Setup",
    "description": "Initialize project structure",
    "acceptance_criteria": ["Project structure created", "Dependencies installed"],
    "blocked_by": null
  },
  {
    "title": "[Slice 2] Models",
    "description": "Create domain models",
    "acceptance_criteria": ["Models defined", "Validators implemented"],
    "blocked_by": 1
  }
]
```

### Output

```
Creating GitHub issues for vamsikrish96/expense-approval...

✓ Issue #1: [Slice 1] Foundation Setup
  https://github.com/vamsikrish96/expense-approval/issues/1

✓ Issue #2: [Slice 2] Models (blocked by #1)
  https://github.com/vamsikrish96/expense-approval/issues/2

2 issues created successfully!
```

## Features

✓ **Dependency ordering** - Creates blocker issues first, allowing forward references
✓ **Blocking links** - Establishes "Blocked by" relationships between issues
✓ **Formatting** - Consistently formats all issues with acceptance criteria
✓ **Labels** - Adds configurable labels (triage, priority, etc.)
✓ **Validation** - Validates input before creating issues
✓ **Error handling** - Clear error messages if creation fails

## Requirements

- GitHub repository must exist
- User must have push/write access to create issues
- GitHub authentication configured (SSH key or token)

## Integration with /to-issues

This skill complements `/to-issues`:

1. **Design phase**: Use `/to-issues` to break down work into slices
2. **Review phase**: Discuss and refine slices with stakeholders
3. **Finalize phase**: Use `/publish-issues` to create GitHub issues

## Advanced Options

### Custom Labels

```bash
/publish-issues owner/repo --labels "priority:high,type:feature" slices.json
```

### Milestone Assignment

```bash
/publish-issues owner/repo --milestone "v1.0" slices.json
```

### Custom Issue Template

```bash
/publish-issues owner/repo --template custom-template.md slices.json
```

## Tips

- **Organize slices first**: Use `/to-issues` to refine before publishing
- **Review blockers**: Ensure blocking relationships are correct before publishing
- **Use consistent naming**: Keep slice titles consistent across documentation
- **Label your slices**: Use labels to organize by priority, type, or team
- **Batch creation**: Create all related slices at once to maintain consistency

## Notes

- Issues are created in the order specified (or dependency order if using `--order-by-dependencies`)
- Blocking relationships use GitHub issue references (e.g., "Blocked by #1")
- All created issues are returned with their URLs for reference
- Existing issues are NOT modified (safe to re-run with updated slices)
