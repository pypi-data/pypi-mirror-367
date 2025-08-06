# boot/core/file_packager.py
"""
Parses raw LLM text output into a structured list of files.
"""

import re
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import List, Tuple

# Regex to find a file block, capturing the path, language hint, and content.
# The key fix is adding the (?m) multiline flag at the start, so that `^`
# matches the beginning of each line, not just the start of the string.
FILE_BLOCK_RE = re.compile(
    r"(?ms)^\s*###\s*FILE:\s*(?P<path>[^\r\n]+)\r?\n```(?P<lang>[^\r\n`]*)\r?\n(?P<content>.*?)\r?\n```"
)

# ... the rest of the file remains the same ...

# Regex to detect if a string is fully wrapped in a markdown code fence.
FULL_FENCE_RE = re.compile(r"(?s)^\s*```[a-zA-Z0-9_-]*\s*\r?\n(.*)\r?\n```\s*$")
# Regex to find and remove a leading `### FILE:` marker from content.
FILE_MARKER_RE = re.compile(r"(?m)^\s*###\s+FILE:.*\r?\n")
# Regex to remove a leading Byte Order Mark (BOM), sometimes added by models.
LEADING_BOM_RE = re.compile(r"^\ufeff")

MARKDOWN_EXTS = (".md", ".markdown", ".rst")


@dataclass
class PackedFile:
    """A simple data class to hold a parsed file's path and content."""

    path: str
    content: str


def _normalize_newlines(s: str) -> str:
    """Normalizes all newline variations (CRLF, CR) to a single LF."""
    return s.replace("\r\n", "\n").replace("\r", "\n")


def _strip_bom(s: str) -> str:
    """Removes the Byte Order Mark from the beginning of a string, if present."""
    return LEADING_BOM_RE.sub("", s)


def _is_markdown_like(path: str) -> bool:
    """Checks if a file path has a markdown-like extension."""
    return path.lower().endswith(MARKDOWN_EXTS)


def _strip_leading_file_marker(s: str) -> str:
    """Removes the first occurrence of a `### FILE:` marker line."""
    return FILE_MARKER_RE.sub("", s, count=1)


def _strip_full_file_fence_if_wrapped(s: str) -> str | None:
    """If content is wrapped in a single, full-file fence, strips it."""
    m = FULL_FENCE_RE.match(s)
    return m.group(1) if m else None


def _sanitize_path(raw_path: str) -> str | None:
    """
    Cleans and validates a raw file path from the LLM.
    """
    p = raw_path.replace("\\", "/").strip()
    if not p or p.startswith("./") or p.startswith("templates/"):
        return None

    pp = PurePosixPath(p)
    if pp.is_absolute() or any(part == ".." for part in pp.parts):
        return None

    return str(pp)


def _sanitize_content(path: str, content: str) -> str:
    """
    Cleans the raw content string from the LLM.
    """
    s = _normalize_newlines(_strip_bom(content))
    if _is_markdown_like(path):
        return s

    no_marker = _strip_leading_file_marker(s)
    inner = _strip_full_file_fence_if_wrapped(no_marker)
    return _normalize_newlines(inner) if inner is not None else no_marker


def pack_from_raw(raw_text: str) -> Tuple[List[PackedFile], List[str]]:
    """
    Parses raw LLM generation text into a list of PackedFile objects.
    """
    diagnostics: List[str] = []
    blocks = list(FILE_BLOCK_RE.finditer(raw_text))
    if not blocks:
        diagnostics.append(
            "Warning: No '### FILE:' blocks were found in the LLM response."
        )
        return [], diagnostics

    files: dict[str, str] = {}
    for m in blocks:
        raw_path = m.group("path").strip()
        content = m.group("content")

        path = _sanitize_path(raw_path)
        if not path:
            diagnostics.append(f"Skipped invalid or disallowed path: {raw_path!r}")
            continue

        cleaned_content = _sanitize_content(path, content)

        if path in files:
            diagnostics.append(f"Warning: Duplicate path found, overwriting: {path}")
        files[path] = cleaned_content

    return [PackedFile(k, v) for k, v in files.items()], diagnostics
