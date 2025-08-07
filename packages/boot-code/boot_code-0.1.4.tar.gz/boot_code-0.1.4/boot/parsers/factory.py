# FILE: boot/parsers/factory.py
"""
Factory for creating language-specific error parsers.
"""

from .languages.python import PythonErrorParser  # Import the new parser
from .languages.rust import RustErrorParser
from .types import ErrorParser


class DefaultParser(ErrorParser):
    """A fallback parser that truncates the log and extracts 'error:' lines."""

    def parse(self, error_log: str) -> str:
        """Extracts lines containing 'error' and truncates the log."""
        error_lines = [
            line for line in error_log.splitlines() if "error" in line.lower()
        ]
        if error_lines:
            # Return up to 15 most relevant lines.
            return "\n".join(error_lines[:15])
        # If no 'error' lines, just truncate the full log.
        return error_log[:2000] + "\n..." if len(error_log) > 2000 else error_log


# The registry maps language names to their specific parser class.
PARSER_REGISTRY: dict[str, type[ErrorParser]] = {
    "rust": RustErrorParser,
    "python": PythonErrorParser,  # Add the new Python parser here
}


def create_parser(language: str) -> ErrorParser:
    """
    Instantiates and returns the correct error parser for the given language.

    Args:
        language: The language of the project (e.g., 'rust', 'python').

    Returns:
        An instance of the appropriate ErrorParser, or a DefaultParser if
        no specific parser is registered for that language.
    """
    lang_lower = language.lower()
    parser_class = PARSER_REGISTRY.get(lang_lower, DefaultParser)
    return parser_class()
