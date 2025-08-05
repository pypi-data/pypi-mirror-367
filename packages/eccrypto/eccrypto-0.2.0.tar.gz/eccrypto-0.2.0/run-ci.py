import subprocess
import sys
import time

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Initialize the rich console
console = Console()

# The list of commands for your CI pipeline
CI_COMMANDS = [
    "uv run ruff check . --fix",
    "uv run ruff check --select I --fix",
    "uv run ruff format .",
    "uv run pytest",
    "uv run pyright .",
]


def run_command(command: str) -> tuple[bool, str]:
    """Runs a command and captures its output."""
    process = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
    )
    return process.returncode == 0, process.stdout + process.stderr


def main():
    """Runs the CI checks with a sequential, pipeline-style output."""
    console.print(Panel("🚀 Starting CI Pipeline", style="bold blue", expand=False))

    start_time = time.time()

    for i, command in enumerate(CI_COMMANDS):
        # The 'step_title' variable was removed from here.
        with console.status(
            f"[bold yellow]Running '{command}'...[/bold yellow]", spinner="dots"
        ):
            success, output = run_command(command)

        if success:
            console.print(f"✅ [bold green]Passed[/bold green]: {command}")
        else:
            console.print(f"❌ [bold red]Failed[/bold red]: {command}")
            console.print("     [red]↓[/red]")

            error_panel = Panel(
                Text(output.strip(), style="white"),
                title="[bold red]Error Output[/bold red]",
                border_style="red",
                expand=True,
            )
            console.print(error_panel)
            sys.exit(1)

        if i < len(CI_COMMANDS) - 1:
            console.print("     [blue]↓[/blue]")

    total_time = f"{time.time() - start_time:.2f}"
    console.print(
        Panel(
            f"✅ All checks passed successfully in {total_time}s!",
            style="bold green",
            expand=False,
        )
    )


if __name__ == "__main__":
    main()
