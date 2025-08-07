import os
import sys
import subprocess
import time
from pathlib import Path
from rich.console import Console
from rich.progress import Progress
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

from fenix import __version__

console = Console()

TEMPLATE_APP = '''from fenix import App

app = App()

@app.route("/")
def home():
    return app.render("home", name="Azeem")

app.run()
'''

TEMPLATE_HTML = '''{% template "home" %}
<html>
<body>
    <h1>Hello {{ name }}!</h1>
</body>
</html>
'''

def welcome():
    console.print(Panel.fit(
        "[bold cyan]🚀 Welcome to FeniX Framework![/bold cyan]\n"
        "[green]Fast. Minimal. Future Ready.[/green]\n"
        "Type: [yellow]fx --help[/yellow] for commands",
        title="[bold red]FeniX CLI[/bold red]",
        border_style="blue"
    ))

def show_version():
    console.print(f"[bold green]FeniX Framework v{__version__}[/bold green]")

def make_project():
    if Path("app.py").exists() or Path("templates.html").exists():
        console.print("[bold red]⚠ Project already exists in this folder![/bold red]")
        return

    with Progress() as progress:
        task = progress.add_task("[cyan]Creating project files...", total=100)
        time.sleep(0.3)
        with open("app.py", "w") as f:
            f.write(TEMPLATE_APP)
        progress.update(task, advance=50)
        time.sleep(0.3)
        with open("templates.html", "w") as f:
            f.write(TEMPLATE_HTML)
        progress.update(task, advance=50)

    console.print("[bold green]✅ Project created successfully![/bold green]")

    # Show folder structure
    tree = Tree("📂 [bold blue]Project Structure[/bold blue]")
    tree.add("app.py")
    tree.add("templates.html")
    console.print(tree)

def run_server():
    if not Path("app.py").exists():
        console.print("[bold red]❌ app.py not found in current directory![/bold red]")
        return

    console.print("[bold yellow]🚀 Starting FeniX server...[/bold yellow]")
    subprocess.run([sys.executable, "app.py"])

def main():
    if len(sys.argv) == 1:
        welcome()
        return

    command = sys.argv[1]

    if command == "version":
        show_version()

    elif command == "make":
        if len(sys.argv) > 2 and sys.argv[2] == "project":
            make_project()
        else:
            console.print("[bold red]Usage: fx make project[/bold red]")

    elif command == "server":
        run_server()

    else:
        console.print(f"[bold red]Unknown command:[/bold red] {command}")
