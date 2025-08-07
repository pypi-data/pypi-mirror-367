# FILE: boot/parsers/languages/python.py
"""A concrete ErrorParser implementation for Python build and runtime errors."""

import re
from typing import List

from boot.parsers.types import ErrorParser


class PythonErrorParser(ErrorParser):
    """
    Parses common Python errors from sources like Poetry, Ruff, and pytest.

    This parser prioritizes extracting the most actionable error messages and
    the relevant lines from tracebacks to provide a concise summary for the LLM.
    It looks for common, high-impact errors first.
    """

    # Regex to find the final, most specific error line in a standard traceback
    TRACEBACK_FINAL_ERROR_RE = re.compile(r"^\w*Error:.*$", re.MULTILINE)

    def _find_poetry_errors(self, error_log: str) -> List[str]:
        """Looks for common, critical errors from Poetry dependency management."""
        found = []
        if "SolverProblemError" in error_log:
            found.append(
                "Poetry SolverProblemError: A dependency conflict occurred. "
                "The versions listed in pyproject.toml are incompatible."
            )
        if "PackageNotFound" in error_log:
            found.append(
                "Poetry PackageNotFound: A package specified in pyproject.toml could not be found on PyPI."
            )
        return found

    def _find_import_errors(self, error_log: str) -> List[str]:
        """Extracts ModuleNotFoundError and ImportError lines."""
        return re.findall(
            r"^(?:ModuleNotFoundError|ImportError):.*$", error_log, re.MULTILINE
        )

    def _find_syntax_errors(self, error_log: str) -> str | None:
        """Extracts the full block for a SyntaxError, which is highly specific."""
        match = re.search(
            r"File \"(.*)\", line (\d+)\n(?:.*\n){1,2}(\s*\^\s*\n)?SyntaxError: (.*)",
            error_log,
        )
        if match:
            return f"SyntaxError in {match.group(1)} on line {match.group(2)}: {match.group(4)}"
        return None

    def parse(self, error_log: str) -> str:
        """
        Parses a raw Python error log and extracts the most relevant information.

        Args:
            error_log: The complete stderr/stdout from a failed command.

        Returns:
            A concise, actionable summary of the failure.
        """
        # Priority 1: Poetry dependency errors are often the root cause.
        poetry_errors = self._find_poetry_errors(error_log)
        if poetry_errors:
            return "Key Errors (Dependency Issues):\n" + "\n".join(poetry_errors)

        # Priority 2: Syntax errors are specific and need to be fixed first.
        syntax_error = self._find_syntax_errors(error_log)
        if syntax_error:
            return f"Key Error (Build Stopper):\n{syntax_error}"

        # Priority 3: Import errors are the next most common issue.
        import_errors = self._find_import_errors(error_log)
        if import_errors:
            return "Key Errors (Import Issues):\n" + "\n".join(import_errors)

        # Priority 4: Find the last, most specific error in a standard traceback.
        final_traceback_errors = self.TRACEBACK_FINAL_ERROR_RE.findall(error_log)
        if final_traceback_errors:
            # Return the last 3 lines, which are usually the most specific.
            return "Key Errors (Runtime Traceback):\n" + "\n".join(
                final_traceback_errors[-3:]
            )

        # Fallback: If no specific patterns match, return a truncated log.
        return error_log[:2000] + "\n..." if len(error_log) > 2000 else error_log
