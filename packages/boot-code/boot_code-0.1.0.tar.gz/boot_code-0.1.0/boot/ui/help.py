import click
import pyfiglet
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


class RichHelpGroup(click.Group):
    """A custom click.Group class that uses Rich to format the help screen."""

    def format_help(self, ctx: click.Context, formatter: click.HelpFormatter) -> None:
        """Overrides the default help formatting to render a custom screen."""
        console = Console()
        console.print()

        # 1. Banner
        banner = pyfiglet.figlet_format("boot", font="colossal")
        console.print(Text(banner, style="bold cyan"))

        # 2. Tagline
        tagline = "Your AI-powered data pipeline generator."
        console.print(Align.center(Text(tagline, style="bold")))
        console.print()

        # 3. Usage
        usage_table = Table.grid(padding=(0, 1))
        usage_table.add_column(style="yellow bold")
        usage_table.add_column()
        usage_table.add_row("USAGE:", Text("boot <command> [options]", style="white"))
        console.print(usage_table)
        console.print()

        # 4. Commands Table
        commands_table = Table(
            box=None, expand=True, show_header=False, show_edge=False, padding=(0, 2)
        )
        commands_table.add_column(style="cyan", no_wrap=True)
        commands_table.add_column()

        # Get commands from the click context
        for command in self.list_commands(ctx):
            cmd_obj = self.get_command(ctx, command)
            if cmd_obj:
                commands_table.add_row(command, cmd_obj.get_short_help_str())

        console.print(
            Panel(commands_table, title="[yellow bold]COMMANDS", border_style="dim")
        )
        console.print()

        # 5. Options Table
        options_table = Table(
            box=None, expand=True, show_header=False, show_edge=False, padding=(0, 2)
        )
        options_table.add_column(style="cyan", no_wrap=True)
        options_table.add_column()

        # Get options from the click context
        for param in self.get_params(ctx):
            if isinstance(param, click.Option):
                # Format option names like "-v, --version"
                names = ", ".join(param.opts)
                options_table.add_row(names, param.help)

        console.print(
            Panel(
                options_table, title="[yellow bold]GLOBAL OPTIONS", border_style="dim"
            )
        )
        console.print()

        # 6. Example
        example_panel = Panel(
            Text("boot generate path/to/spec.toml --two-pass", style="cyan"),
            title="[yellow bold]EXAMPLE",
            border_style="dim",
        )
        console.print(example_panel)
        console.print()
