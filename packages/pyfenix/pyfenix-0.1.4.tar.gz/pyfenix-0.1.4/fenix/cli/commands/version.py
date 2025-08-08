# fenix/cli/commands/version.py

from rich.console import Console
from tfenix import __version__

console = Console()

def show():
    console.print(f"[bold green]FeniX Framework v{__version__}[/bold green]")
