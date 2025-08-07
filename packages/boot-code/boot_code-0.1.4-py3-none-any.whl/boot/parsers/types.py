# FILE: boot/parsers/types.py
"""
Defines the core interfaces and data structures for error parsers.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class ErrorParser(Protocol):
    """
    The interface (Strategy) for a language-specific error log parser.

    The goal of a parser is to reduce a verbose compiler log into a short,
    succinct summary of the most critical, actionable errors for an LLM.
    """

    def parse(self, error_log: str) -> str:
        """
        Parses a raw compiler error log.

        Args:
            error_log: The full stdout/stderr from a failed build command.

        Returns:
            A concise string containing only the most critical errors.
        """
        ...
