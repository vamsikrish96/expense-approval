#!/usr/bin/env python3
"""
Skill: /implement-slices
Implement feature slices with testing and progress tracking.
"""

import sys
import json
import subprocess
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class FeatureSlice:
    """Represents a feature slice."""
    number: int
    title: str
    description: str = ""
    acceptance_criteria: List[str] = field(default_factory=list)
    blocked_by: Optional[int] = None
    test_file: Optional[str] = None
    test_pattern: Optional[str] = None
    status: str = "pending"  # pending, in_progress, completed, failed
    tests_run: int = 0
    tests_passed: int = 0
    tests_failed: int = 0
    commit_hash: Optional[str] = None
    error_message: Optional[str] = None


class SliceImplementor:
    """Implements feature slices with testing and progress tracking."""

    def __init__(self, repo: str, progress_file: str = "PROGRESS.md"):
        """
        Initialize implementor.

        Args:
            repo: GitHub repository (owner/repo)
            progress_file: Path to progress file
        """
        self.repo = repo
        self.progress_file = Path(progress_file)
        self.slices: List[FeatureSlice] = []
        self.start_time = datetime.utcnow()

    def add_slice(self, slice_obj: FeatureSlice) -> None:
        """Add a slice to implement."""
        self.slices.append(slice_obj)

    def install_requirements(self) -> bool:
        """Install requirements.txt."""
        print("Installing requirements...")
        try:
            result = subprocess.run(
                ["pip", "install", "-r", "requirements.txt"],
                capture_output=True,
                text=True,
                timeout=300
            )
            if result.returncode == 0:
                print("✓ requirements.txt installed\n")
                return True
            else:
                print(f"✗ Failed to install requirements:\n{result.stderr}")
                return False
        except Exception as e:
            print(f"✗ Error installing requirements: {e}")
            return False

    def run_tests(self, slice_obj: FeatureSlice) -> Tuple[bool, int, int]:
        """
        Run tests for a slice.

        Returns:
            (success, tests_passed, tests_failed)
        """
        if not slice_obj.test_file:
            print(f"  → No test file configured, skipping tests")
            return True, 0, 0

        print(f"  → Running tests: {slice_obj.test_file}...", end="")

        try:
            # Build pytest command
            cmd = ["python", "-m", "pytest", slice_obj.test_file, "-v", "--tb=short"]
            if slice_obj.test_pattern:
                cmd.append(f"-k={slice_obj.test_pattern}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )

            # Parse output
            output = result.stdout + result.stderr
            passed = output.count(" PASSED")
            failed = output.count(" FAILED")

            if result.returncode == 0:
                print(f"\n  ✓ {passed} tests passed")
                return True, passed, failed
            else:
                print(f"\n  ✗ {failed} tests failed")
                slice_obj.error_message = output[-500:]  # Last 500 chars
                return False, passed, failed

        except subprocess.TimeoutExpired:
            print("\n  ✗ Tests timed out")
            slice_obj.error_message = "Tests timed out after 300 seconds"
            return False, 0, 0
        except Exception as e:
            print(f"\n  ✗ Error running tests: {e}")
            slice_obj.error_message = str(e)
            return False, 0, 0

    def commit_changes(self, slice_obj: FeatureSlice) -> Optional[str]:
        """
        Commit changes for a slice.

        Returns:
            Commit hash if successful, None otherwise
        """
        print("  → Committing changes...", end="")

        try:
            # Stage all changes
            subprocess.run(
                ["git", "add", "-A"],
                capture_output=True,
                timeout=30
            )

            # Create commit
            commit_msg = f"""Implement {slice_obj.title}

Slice #{slice_obj.number}: {slice_obj.description[:100]}

Tests: {slice_obj.tests_passed}/{slice_obj.tests_passed + slice_obj.tests_failed} passed

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"""

            result = subprocess.run(
                ["git", "commit", "-m", commit_msg],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                # Extract commit hash
                output = result.stdout
                if "create mode" in output or "insertions" in output:
                    # Get latest commit hash
                    hash_result = subprocess.run(
                        ["git", "rev-parse", "HEAD"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    commit_hash = hash_result.stdout.strip()[:8]
                    print(f"\n  ✓ Committed ({commit_hash})")
                    return commit_hash
                else:
                    print("\n  → No changes to commit")
                    return None
            else:
                # Maybe no changes
                if "nothing to commit" in result.stdout:
                    print("\n  → No changes to commit")
                    return None
                else:
                    print(f"\n  ✗ Commit failed: {result.stderr[:100]}")
                    return None

        except Exception as e:
            print(f"\n  ✗ Error during commit: {e}")
            return None

    def implement_slice(self, slice_obj: FeatureSlice) -> bool:
        """Implement a single slice."""
        print(f"\n[{slice_obj.number}/{len(self.slices)}] {slice_obj.title}")

        # Update status
        slice_obj.status = "in_progress"

        # Run tests
        success, passed, failed = self.run_tests(slice_obj)
        slice_obj.tests_passed = passed
        slice_obj.tests_failed = failed

        if not success:
            slice_obj.status = "failed"
            print(f"  ✗ Implementation failed - tests did not pass")
            return False

        # Commit changes
        if success:
            commit_hash = self.commit_changes(slice_obj)
            if commit_hash:
                slice_obj.commit_hash = commit_hash

        # Mark as completed
        slice_obj.status = "completed"
        print(f"  → Marking as completed")

        return True

    def update_progress(self) -> None:
        """Update PROGRESS.md with current status."""
        # Calculate summary
        total = len(self.slices)
        completed = sum(1 for s in self.slices if s.status == "completed")
        in_progress = sum(1 for s in self.slices if s.status == "in_progress")
        pending = sum(1 for s in self.slices if s.status == "pending")
        failed = sum(1 for s in self.slices if s.status == "failed")

        # Build progress file
        lines = [
            "# Implementation Progress\n",
            f"**Last Updated**: {datetime.utcnow().isoformat()}Z\n",
            "\n## Summary\n",
            f"- Total Slices: {total}\n",
            f"- Completed: {completed}\n",
            f"- In Progress: {in_progress}\n",
            f"- Pending: {pending}\n",
            f"- Failed: {failed}\n",
            "\n## Status by Slice\n",
        ]

        # Add status for each slice
        for slice_obj in self.slices:
            status_icon = {
                "completed": "✅",
                "in_progress": "🔄",
                "pending": "⏳",
                "failed": "❌",
            }.get(slice_obj.status, "❓")

            lines.append(f"\n### {status_icon} {slice_obj.title}\n")
            lines.append(f"\n- **Status**: {slice_obj.status}\n")

            if slice_obj.tests_passed or slice_obj.tests_failed:
                total_tests = slice_obj.tests_passed + slice_obj.tests_failed
                lines.append(f"- **Tests**: Passed ({slice_obj.tests_passed}/{total_tests})\n")

            if slice_obj.commit_hash:
                lines.append(f"- **Committed**: {datetime.utcnow().isoformat()}\n")
                lines.append(f"- **Commit**: {slice_obj.commit_hash}\n")

            if slice_obj.error_message:
                lines.append(f"- **Error**: {slice_obj.error_message[:100]}\n")

        # Write file
        with open(self.progress_file, 'w') as f:
            f.writelines(lines)

        print(f"\nProgress saved to {self.progress_file}")

    def implement_all(self) -> bool:
        """Implement all slices."""
        print(f"Implementing feature slices for {self.repo}...\n")

        # Install requirements once
        if not self.install_requirements():
            return False

        # Implement each slice
        all_success = True
        for slice_obj in self.slices:
            # Check if blocked
            if slice_obj.blocked_by:
                blocker = next((s for s in self.slices if s.number == slice_obj.blocked_by), None)
                if blocker and blocker.status != "completed":
                    print(f"\n[{slice_obj.number}/{len(self.slices)}] {slice_obj.title}")
                    print(f"  ⏳ Blocked by #{slice_obj.blocked_by}")
                    continue

            # Implement
            success = self.implement_slice(slice_obj)
            if not success:
                all_success = False

        # Update progress
        self.update_progress()

        # Summary
        completed = sum(1 for s in self.slices if s.status == "completed")
        print(f"\n{'='*60}")
        print(f"Implementation Summary: {completed}/{len(self.slices)} slices completed")
        print(f"{'='*60}")

        return all_success


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Implement feature slices with testing and progress tracking"
    )
    parser.add_argument("--repo", required=True, help="GitHub repository (owner/repo)")
    parser.add_argument(
        "--progress-file",
        default="PROGRESS.md",
        help="Path to progress file"
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip running tests"
    )
    parser.add_argument(
        "--no-commit",
        action="store_true",
        help="Don't commit changes"
    )

    args = parser.parse_args()

    # Create implementor
    implementor = SliceImplementor(args.repo, args.progress_file)

    # Add example slices (in real implementation, would read from GitHub issues)
    example_slices = [
        FeatureSlice(
            number=1,
            title="[Slice 1] Foundation: Project Setup & Auth Middleware",
            description="Set up FastAPI with mocked Entra ID JWT auth",
            test_file="tests/test_auth.py",
            acceptance_criteria=[
                "FastAPI app runs on port 8000",
                "JWT token parser works",
                "Auth middleware extracts claims",
            ]
        ),
        FeatureSlice(
            number=2,
            title="[Slice 2] Domain Models & Validation",
            description="Create Pydantic models with validation",
            test_file="tests/test_models.py",
            blocked_by=1,
            acceptance_criteria=[
                "Expense model with validators",
                "AuditLog model defined",
            ]
        ),
        FeatureSlice(
            number=3,
            title="[Slice 3] In-Memory Database Layer",
            description="Implement database with CRUD operations",
            test_file="tests/test_workflows.py",
            test_pattern="database",
            blocked_by=2,
        ),
    ]

    for slice_obj in example_slices:
        implementor.add_slice(slice_obj)

    # Implement all
    success = implementor.implement_all()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
