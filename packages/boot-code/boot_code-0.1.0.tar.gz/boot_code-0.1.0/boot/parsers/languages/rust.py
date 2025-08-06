# FILE: boot/parsers/languages/rust.py
"""A concrete ErrorParser implementation for Rust's `cargo build` output."""

import re
from typing import List

from boot.parsers.types import ErrorParser


class RustErrorParser(ErrorParser):
    """
    Parses `cargo build` output to find the most critical errors.

    This parser is designed to extract the full, multi-line error blocks from
    the compiler output, which are more useful for an LLM than single lines.
    It prioritizes errors in this order:
    1. Unresolved imports or modules (often the root cause).
    2. Trait bound errors (a common complex issue).
    3. Any other primary error blocks.
    """

    RUSTC_VERSION_RE = re.compile(r"requires rustc ([\d\.]+) or newer")
    ERROR_SPLIT_RE = re.compile(r"\n(?=error(?:\[E\d+\])?:)")

    def _find_errors_with_keywords(
        self, error_chunks: List[str], keywords: List[str]
    ) -> List[str]:
        """
        Filters a list of error chunks to find those containing specific keywords.

        Args:
            error_chunks: A list of multi-line strings, each an error block.
            keywords: A list of keywords to search for.

        Returns:
            A list of error chunks that contain any of the keywords.
        """
        found = []
        for chunk in error_chunks:
            if any(keyword in chunk for keyword in keywords):
                found.append(chunk.strip())
        return found

    def parse(self, error_log: str) -> str:
        """
        Parses a raw `cargo build` error log and extracts the most relevant
        information for an LLM to perform a fix.

        Args:
            error_log: The complete stderr/stdout from the `cargo build` command.

        Returns:
            A concise, actionable summary of the build failure, including full error blocks.
        """
        # Priority 1: Check for a compiler version mismatch. This is an environment issue.
        version_match = self.RUSTC_VERSION_RE.search(error_log)
        if version_match:
            required_version = version_match.group(1)
            return (
                f"CRITICAL BUILD ERROR: Environment Mismatch.\n"
                f"The code requires Rust compiler version {required_version} or newer. "
                f"The build environment may be using an older version."
            )

        # Split the log into full error blocks.
        chunks = self.ERROR_SPLIT_RE.split(error_log)

        # Priority 2: Look for unresolved imports/modules.
        unresolved_errors = self._find_errors_with_keywords(
            chunks, ["unresolved import", "unresolved module", "failed to resolve"]
        )
        if unresolved_errors:
            return "Key Errors (Unresolved Imports):\n" + "\n---\n".join(
                unresolved_errors[:3]
            )

        # Priority 3: Look for trait bound errors.
        trait_errors = self._find_errors_with_keywords(
            chunks, ["trait bound", "is not satisfied"]
        )
        if trait_errors:
            return "Key Errors (Trait Bounds):\n" + "\n---\n".join(trait_errors[:3])

        # Fallback: Grab the first few generic primary error blocks.
        if chunks:
            generic_errors = [
                chunk.strip() for chunk in chunks if chunk.strip().startswith("error")
            ]
            if generic_errors:
                return "Key Errors:\n" + "\n---\n".join(generic_errors[:3])

        # If no primary errors are found, use the default truncation.
        return error_log[:2000] + "\n..." if len(error_log) > 2000 else error_log
