# FILE: boot/ui/console.py
"""Manages styled and interactive console output using the Rich library."""

import time

from rich.console import Console, RenderableType
from rich.status import Status

# A single, shared Console instance for all UI components.
console = Console()


class ConsoleManager:
    """Manages styled and interactive console output using Rich."""

    def __init__(self) -> None:
        """Initializes the console manager state."""
        self._current_status: Status | None = None
        self._current_text: str = ""
        self._start_time: float = 0.0

    def start_step(self, text: str) -> None:
        """Completes the previous step and starts a new one with an active spinner."""
        if self._current_status:
            self.complete_step()

        self._current_text = text
        self._start_time = time.time()
        self._current_status = console.status(f"  {text}")
        self._current_status.start()

    def complete_step(self, message: str | None = None) -> None:
        """Stops the current spinner and prints a success message with duration."""
        if not self._current_status:
            return

        self._current_status.stop()
        duration = time.time() - self._start_time
        text = message or self._current_text
        console.print(f"✔︎ {text} [{duration:.1f}s]")
        self._current_status = None
        self._current_text = ""

    def fail_step(self, message: str | None = None) -> None:
        """Stops the current spinner and prints a failure message with duration."""
        if not self._current_status:
            return

        self._current_status.stop()
        duration = time.time() - self._start_time
        text = message or self._current_text
        console.print(f"✖︎ {text} [{duration:.1f}s]")
        self._current_status = None
        self._current_text = ""

    def print_error(self, message: str) -> None:
        """Prints a formatted error message."""
        if self._current_status:
            self.fail_step()
        console.print(f"\n[bold red]Error:[/bold red] {message}")

    def print_warning(self, message: str) -> None:
        """Prints a formatted, non-critical warning message."""
        console.print(f"  [yellow]Warning:[/yellow] {message}")

    def print_info(self, message: str) -> None:
        """Prints a formatted informational message."""
        console.print(f"  [bold blue]i[/bold blue] {message}")

    def print_summary(self, summary_table: RenderableType) -> None:
        """Prints a final summary object (e.g., a Rich Table or Panel)."""
        console.print(summary_table)

    def print_header(self, text: str) -> None:
        """Prints a styled header message."""
        console.print(f"\n[bold cyan]{text}[/bold cyan]")
