# FILE: boot/cli.py

from __future__ import annotations

import asyncio
from pathlib import Path

import click
import pyfiglet
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from boot import __version__
from boot.errors import GenerationError, SpecValidationError
from boot.models.config import get_settings
from boot.models.spec import SpexSpecification
from boot.services import GeneratorService
from boot.ui.console import ConsoleManager
from boot.ui.help import RichHelpGroup


# Removed `no_args_is_help=True` which conflicts with `invoke_without_command=True`
@click.group(cls=RichHelpGroup, invoke_without_command=True)
@click.version_option(
    __version__, "-v", "--version", message="%(prog)s version %(version)s"
)
@click.pass_context
def cli(ctx: click.Context) -> None:
    """Spex uses AI to generate production-ready data pipelines from simple specifications."""
    # This callback now correctly handles the case where no subcommand is given.
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        ctx.exit(0)


@cli.command()
@click.argument(
    "spec_file", type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
@click.option(
    "-o",
    "--output-dir",
    type=click.Path(file_okay=False, path_type=Path),
    default=None,
    help="Directory to write the generated project.",
)
@click.option(
    "--provider",
    type=click.Choice(["openai", "gemini"]),
    help="LLM provider to use. Overrides .env settings.",
)
@click.option("--api-key", help="API key for the selected provider. Overrides .env.")
@click.option(
    "--model",
    help="Specific model identifier (e.g., 'gpt-4o-mini', 'gemini-1.5-flash-latest').",
)
@click.option(
    "--two-pass",
    is_flag=True,
    default=None,
    help="Enable a second LLM pass for code review and refinement.",
)
@click.option(
    "--build-pass",
    is_flag=True,
    default=None,
    help="EXPERIMENTAL: Attempt to build and automatically fix the generated code.",
)
@click.option("--timeout", type=int, help="Timeout in seconds for API requests.")
@click.option(
    "--temperature",
    type=click.FloatRange(0.0, 2.0),
    help="Generation temperature (e.g., 0.1 for deterministic, 1.0 for creative).",
)
def generate(
    spec_file: Path,
    output_dir: Path | None,
    provider: str | None,
    api_key: str | None,
    model: str | None,
    two_pass: bool | None,
    build_pass: bool | None,
    timeout: int | None,
    temperature: float | None,
) -> None:
    """Generate a new project from a spec file."""
    console = Console()
    manager = ConsoleManager()

    try:
        settings = get_settings(
            provider=provider,
            api_key=api_key,
            model=model,
            timeout=timeout,
            two_pass=two_pass,
            output_dir=output_dir,
            temperature=temperature,
            build_pass=build_pass,
        )
        service = GeneratorService(settings)

        console.print(
            pyfiglet.figlet_format("boot", font="colossal"), style="bold cyan"
        )

        summary_table = Table(box=None, show_header=False)
        summary_table.add_column(style="bold cyan")
        summary_table.add_column()
        summary_table.add_row("Provider:", settings.provider)
        summary_table.add_row("Model:", settings.get_model())
        summary_table.add_row(
            "Review Pass:", "Enabled" if settings.two_pass else "Disabled"
        )
        summary_table.add_row(
            "Build Pass:", "Enabled" if settings.build_pass else "Disabled"
        )
        if settings.temperature is not None:
            summary_table.add_row("Temperature:", f"{settings.temperature:.1f}")
        console.print(summary_table)
        console.print()

        generated_path = asyncio.run(service.generate_from_spec(spec_file, manager))

        console.print()
        console.print(
            Panel(
                f"[bold green]✅ Generation complete![/bold green]\n"
                f"Project created in: [cyan]{generated_path.resolve()}[/cyan]",
                title="[bold]Summary[/bold]",
                border_style="green",
            )
        )

        try:
            relative_path = generated_path.resolve().relative_to(Path.cwd().resolve())
        except ValueError:
            relative_path = generated_path

        next_steps = (
            f"1. [bold]cd {relative_path}[/bold]\n"
            f"2. [bold]make build[/bold]\n"
            f"3. [bold]make run[/bold]"
        )
        console.print(
            Panel(next_steps, title="[bold]🚀 Next Steps", border_style="dim")
        )

    except (GenerationError, SpecValidationError) as err:
        manager.fail_step()
        manager.print_error(str(err))
        raise click.exceptions.Exit(1) from err
    except Exception as err:
        manager.fail_step()
        manager.print_error(f"An unexpected error occurred: {err}")
        raise click.exceptions.Exit(1) from err


@cli.command()
@click.argument(
    "spec_file", type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
def validate(spec_file: Path) -> None:
    """Validate the structure and content of a spec file."""
    console = Console()
    try:
        _ = SpexSpecification.from_toml(spec_file)
        console.print(
            f"[bold green]Specification file '{spec_file}' is valid.[/bold green]"
        )
    except SpecValidationError as err:
        console.print(f"[bold red]Validation Error in '{spec_file}':[/bold red]\n{err}")
        raise click.exceptions.Exit(1) from err
    except Exception as err:
        console.print(f"[bold red]Error:[/bold red] {err}")
        raise click.exceptions.Exit(1) from err


if __name__ == "__main__":
    cli(auto_envvar_prefix="SPEX")
