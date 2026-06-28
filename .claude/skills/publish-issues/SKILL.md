# /publish-issues

Create GitHub issues for finalized feature slices.

## Purpose

After finalizing feature slices with `/to-issues`, use this skill to:
1. Parse finalized slices (JSON file or input)
2. Validate slices and blocking relationships
3. Order issues by dependencies (blockers first)
4. Create GitHub issues automatically
5. Establish "Blocked by" links between issues

## Usage

```
/publish-issues --repo owner/repo --file slices.json
```

Or with inline slices:

```
/publish-issues --repo owner/repo --slices '[{...}, {...}]'
```

## Input Format

### JSON File (slices.json)

```json
[
  {
    "title": "[Slice 1] Foundation: Project Setup",
    "description": "Set up FastAPI with mocked Entra ID JWT auth",
    "acceptance_criteria": [
      "FastAPI app initialized",
      "JWT token parser works"
    ],
    "blocked_by": null,
    "labels": ["slice", "foundation"]
  },
  {
    "title": "[Slice 2] Domain Models",
    "description": "Create Pydantic models",
    "acceptance_criteria": ["Models defined"],
    "blocked_by": 1,
    "labels": ["slice"]
  }
]
```

### Required Fields
- `title` - Issue title
- `description` - What to build
- `acceptance_criteria` - Array of acceptance criteria

### Optional Fields
- `blocked_by` - Issue number this depends on
- `labels` - Array of labels to add

## Process

For each slice:
```
1. Parse JSON input
2. Validate structure
   - Check required fields
   - Verify blocked_by references exist
3. Order by dependencies (blockers first)
4. Display preview
5. Create GitHub issues in order
   - Issue #1, #2, etc.
   - Include acceptance criteria
   - Add "Blocked by" section
   - Add labels
6. Print issue URLs
```

## Output

```
Creating GitHub issues for owner/repo...

Slices to create (in order):

1. [Slice 1] Foundation: Project Setup
2. [Slice 2] Domain Models (blocked by #1)
3. [Slice 3] Database Layer (blocked by #2)

✓ Issue #1: [Slice 1] Foundation: Project Setup
  https://github.com/owner/repo/issues/1

✓ Issue #2: [Slice 2] Domain Models (blocked by #1)
  https://github.com/owner/repo/issues/2

✓ Issue #3: [Slice 3] Database Layer (blocked by #2)
  https://github.com/owner/repo/issues/3

3 issues created successfully!
```

## Features

✓ **JSON parsing** - Accepts JSON file or inline slices
✓ **Validation** - Checks structure and blocking references
✓ **Dependency ordering** - Creates blockers first
✓ **GitHub integration** - Creates issues via API
✓ **Blocking links** - Establishes "Blocked by" relationships
✓ **Preview mode** - Shows what will be created before proceeding
✓ **Labels support** - Adds labels to each issue

## Requirements

- GitHub repository must exist
- User has write access to create issues
- GitHub authentication configured (SSH or token)
- JSON format valid

## Workflow Integration

```
/to-issues (design)
     ↓
Review & refine
     ↓
/publish-issues (create issues)
     ↓
/implement-slices (implement)
```

## Tips

- Use `/to-issues` first to design slices
- Review blocking relationships before publishing
- Publish all slices at once for consistency
- Use labels to organize (priority, type, team)
- Safe to re-run - existing issues won't be duplicated

## Notes

- Issues created in dependency order
- Blocking references use GitHub issue numbers (#1, #2, etc.)
- All issue URLs printed at the end
- Existing issues are NOT modified
- Safe to interrupt - can resume with same slices
