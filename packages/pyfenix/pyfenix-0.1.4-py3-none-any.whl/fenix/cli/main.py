# fenix/cli/main.py

import sys
from rich.console import Console
from rich.panel import Panel

from fenix import __version__
from fenix.cli.commands import make, run, version,help as help_cmd

console = Console()

def welcome():
    console.print(Panel.fit(
        "[bold cyan]🚀 Welcome to FeniX Framework![/bold cyan]\n"
        "[green]Fast. Minimal. Future Ready.[/green]\n"
        "Type: [yellow]fx --help[/yellow] for commands",
        title="[bold red]FeniX CLI[/bold red]",
        border_style="blue"
    ))

def main():
    if len(sys.argv) == 1:
        welcome()
        return

    command = sys.argv[1]

    if command == "version":
        version.show()

    elif command == "make":
        if len(sys.argv) > 2 and sys.argv[2] == "project":
            make.create()
        else:
            console.print("[bold red]Usage: fx make project[/bold red]")
    elif command=="help":
        help_cmd.run()

    elif command == "server":
        run.dev_server()

    else:
        console.print(f"[bold red]Unknown command:[/bold red] {command}")
