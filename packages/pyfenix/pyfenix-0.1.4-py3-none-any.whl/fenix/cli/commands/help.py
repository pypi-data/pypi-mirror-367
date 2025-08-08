# fenix/cli/commands/help.py

from rich.console import Console

console = Console()

def run():
    console.print("""
[bold cyan]🛠️ Available Commands in FeniX CLI:[/bold cyan]

  [green]version[/green]         Show framework version
  [green]make project[/green]   Create a new FeniX project
  [green]server[/green]         Run development server
  [green]help[/green]           Show this help message

[bold yellow]Usage Examples:[/bold yellow]
  tfx version
  tfx make project
  tfx server
  tfx help
""")
