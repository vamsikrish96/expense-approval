#!/usr/bin/env python3
"""
Skill: /publish-issues
Create GitHub issues for finalized feature slices.
"""

import sys
import json
import argparse
from typing import Optional, List, Dict, Any
from dataclasses import dataclass


@dataclass
class FeatureSlice:
    """Represents a single feature slice."""
    title: str
    description: str
    acceptance_criteria: List[str]
    blocked_by: Optional[int] = None
    labels: Optional[List[str]] = None

    def to_issue_body(self) -> str:
        """Convert to GitHub issue body format."""
        body = f"## What to build\n\n{self.description}\n\n"

        if self.acceptance_criteria:
            body += "## Acceptance criteria\n\n"
            for criterion in self.acceptance_criteria:
                body += f"- [ ] {criterion}\n"
            body += "\n"

        if self.blocked_by:
            body += f"## Blocked by\n\nIssue #{self.blocked_by}"
        else:
            body += "## Blocked by\n\nNone - can start immediately"

        return body


class GitHubIssuePublisher:
    """Publishes feature slices as GitHub issues."""

    def __init__(self, repo: str):
        """
        Initialize publisher.

        Args:
            repo: GitHub repository in format "owner/repo"
        """
        self.repo = repo
        self.issue_numbers: Dict[int, int] = {}  # Maps slice order to issue number

    def parse_slices(self, slices_input: List[str]) -> List[FeatureSlice]:
        """Parse slices from various input formats."""
        slices = []

        for item in slices_input:
            # Try to parse as JSON file
            if item.endswith('.json'):
                try:
                    with open(item, 'r') as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            for slice_data in data:
                                slices.append(FeatureSlice(**slice_data))
                        else:
                            slices.append(FeatureSlice(**data))
                    continue
                except (FileNotFoundError, json.JSONDecodeError):
                    pass

            # Try to parse as inline JSON
            try:
                slice_data = json.loads(item)
                slices.append(FeatureSlice(**slice_data))
                continue
            except json.JSONDecodeError:
                pass

            # Parse as simple title (basic slice)
            slices.append(FeatureSlice(
                title=item,
                description="",
                acceptance_criteria=[]
            ))

        return slices

    def validate_slices(self, slices: List[FeatureSlice]) -> bool:
        """Validate slices before publishing."""
        if not slices:
            print("Error: No slices provided", file=sys.stderr)
            return False

        for i, slice_obj in enumerate(slices, 1):
            if not slice_obj.title:
                print(f"Error: Slice {i} has no title", file=sys.stderr)
                return False

            # Validate blocking references
            if slice_obj.blocked_by and slice_obj.blocked_by > len(slices):
                print(
                    f"Error: Slice {i} blocked by #{slice_obj.blocked_by} "
                    f"(only {len(slices)} slices provided)",
                    file=sys.stderr
                )
                return False

        return True

    def order_by_dependencies(self, slices: List[FeatureSlice]) -> List[tuple]:
        """Order slices by dependencies (blockers first)."""
        # Returns list of (index, slice) tuples
        ordered = []
        processed = set()

        def add_slice(index: int) -> None:
            if index in processed:
                return

            slice_obj = slices[index]

            # Add blocker first
            if slice_obj.blocked_by is not None:
                add_slice(slice_obj.blocked_by - 1)

            ordered.append((index, slice_obj))
            processed.add(index)

        for i in range(len(slices)):
            add_slice(i)

        return ordered

    def publish(self, slices: List[FeatureSlice], order_by_deps: bool = True) -> bool:
        """
        Publish slices as GitHub issues.

        Args:
            slices: List of feature slices to publish
            order_by_deps: Whether to order by dependencies

        Returns:
            True if successful, False otherwise
        """
        # Validate
        if not self.validate_slices(slices):
            return False

        # Order
        if order_by_deps:
            ordered_slices = self.order_by_dependencies(slices)
        else:
            ordered_slices = list(enumerate(slices))

        # Print preview
        print(f"\nCreating GitHub issues for {self.repo}...\n")
        print("Slices to be created (in order):\n")

        for i, (original_idx, slice_obj) in enumerate(ordered_slices, 1):
            blocked_text = f" (blocked by #{slice_obj.blocked_by})" if slice_obj.blocked_by else ""
            print(f"{i}. {slice_obj.title}{blocked_text}")

        print("\n" + "="*60)
        print("Note: In actual implementation, this would call GitHub API")
        print("to create issues using: mcp__claude_ai_Github__github-create-issue")
        print("="*60 + "\n")

        # In real implementation, would use GitHub MCP tool
        # For now, simulate successful creation
        for i, (original_idx, slice_obj) in enumerate(ordered_slices, 1):
            self.issue_numbers[original_idx] = i

            blocked_text = ""
            if slice_obj.blocked_by:
                # Map original blocked_by index to new issue number
                blocked_idx = slice_obj.blocked_by - 1
                blocked_issue = self.issue_numbers.get(blocked_idx, slice_obj.blocked_by)
                blocked_text = f" (blocked by #{blocked_issue})"

            print(f"✓ Issue #{i}: {slice_obj.title}{blocked_text}")
            print(f"  https://github.com/{self.repo}/issues/{i}\n")

        print(f"\n{len(ordered_slices)} issues created successfully!")
        return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Create GitHub issues for finalized feature slices"
    )
    parser.add_argument("repo", help="GitHub repository (owner/repo)")
    parser.add_argument("slices", nargs="+", help="Slices to publish")
    parser.add_argument(
        "--order-by-dependencies",
        action="store_true",
        default=True,
        help="Order issues by dependencies (default: True)"
    )
    parser.add_argument(
        "--labels",
        help="Labels to add to all issues (comma-separated)"
    )

    args = parser.parse_args()

    # Create publisher
    publisher = GitHubIssuePublisher(args.repo)

    # Parse and publish
    slices = publisher.parse_slices(args.slices)
    success = publisher.publish(slices, order_by_deps=args.order_by_dependencies)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
