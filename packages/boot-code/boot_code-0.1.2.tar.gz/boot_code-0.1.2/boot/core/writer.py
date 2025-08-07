# FILE: boot/core/writer.py
"""
This module contains the core, language-agnostic logic for file system
operations, including writing final project files and interim log files.
"""

from __future__ import annotations

import logging
from pathlib import Path

from boot.core.file_packager import PackedFile

logger = logging.getLogger(__name__)


class ProjectWriter:
    """
    Writes generated files to the filesystem for both final output and debugging.
    """

    def _write_files_to_dir(self, output_dir: Path, files: list[PackedFile]) -> None:
        """A helper to write a list of files to a specified directory."""
        if not files:
            logging.warning(f"No files provided to write to {output_dir}.")
            return

        for file_obj in files:
            file_path = output_dir / file_obj.path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(file_obj.content, "utf-8")
            logging.info(f"Wrote file: {file_path}")

    def write_project_files(
        self,
        output_dir: Path,
        files: list[PackedFile],
    ) -> None:
        """
        Writes the final set of generated code files to the project directory.

        Args:
            output_dir: The root project directory.
            files: A list of the final PackedFile objects.
        """
        self._write_files_to_dir(output_dir, files)

    def write_interim_files(
        self, log_dir: Path, pass_num: int, files: list[PackedFile]
    ) -> None:
        """
        Writes the code files from an intermediate pass to a log subdirectory.

        Args:
            log_dir: The main `_boot_logs` directory.
            pass_num: The current pass number, used to create a subdirectory.
            files: The list of PackedFile objects from this pass.
        """
        interim_dir = log_dir / f"pass_{pass_num}_files"
        interim_dir.mkdir(parents=True, exist_ok=True)
        self._write_files_to_dir(interim_dir, files)
        logging.info(f"Wrote interim files for pass {pass_num} to {interim_dir}")
