import sys
import time
from rich.console import Console
from rich.panel import Panel

from fenix import __version__
from fenix.cli.commands import make, run, version, help as help_cmd

console = Console()

def typing(text: str, delay: float = 0.02, style="white"):
    for char in text:
        console.print(char, end="", style=style, soft_wrap=True)
        time.sleep(delay)
    print()

ASCII_LOGO = '''
███████ ███████ ███    ██ ██ ██   ██ 
██      ██      ████   ██ ██  ██ ██  
█████   █████   ██ ██  ██ ██   ███  
██      ██      ██  ██ ██ ██  ██ ██ 
██      ███████ ██   ████ ██ ██   ██ 
'''

def welcome():
    console.print(Panel.fit(
        f"[bold blue]{ASCII_LOGO}[/bold blue]",
        title="[bold red]FeniX CLI[/bold red]",
        border_style="bright_magenta"
    ))
    typing("🚀 Welcome to FeniX Framework!", 0.04, "bold cyan")
    typing("⚡ Fast. Minimal. Future Ready.", 0.03, "green")
    typing("👉 Type: fx --help to get started", 0.02, "yellow")

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

    elif command == "help":
        help_cmd.run()

    elif command == "server":
        run.dev_server()

    else:
        console.print(f"[bold red]Unknown command:[/bold red] {command}")
