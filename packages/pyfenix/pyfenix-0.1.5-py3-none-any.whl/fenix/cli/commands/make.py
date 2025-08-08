import subprocess
import sys
import time
from pathlib import Path
from rich.console import Console
from rich.tree import Tree
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.text import Text
from typing import List

console = Console()
REQUIRED_LIBS = ["rich",]

TEMPLATE_APP = '''
from fenix import App, run_server

app = App()

@app.route("/")
def home():
    return app.render("home", name="Azeem")

@app.route("/dashboard", middleware=app.auth_required)
def dashboard():
    return "Dashboard - Welcome Azeem"

run_server(app)
'''

TEMPLATE_HTML = '''{% template "home" %}
<html>
<body>
    <h1>Hello {{ name }}!</h1>
</body>
</html>
'''


# 💡 Typing effect function
def typing(text: str, delay: float = 0.02):
    for char in text:
        console.print(char, end="", style="bold cyan")
        time.sleep(delay)
    print()


# 💎 Motivational + Vibes
def show_banner():
    console.print("\n[bold magenta]🚀 Starting Your FeniX Project Setup...[/bold magenta]\n")
    typing("✨ Dreams don't work unless you do...")
    time.sleep(1)
    typing("🛠️  Setting up your environment like a true hacker dev...\n", 0.03)
    time.sleep(1)


# 📦 Install/check requirements
def install_requirements():
    console.print("[bold yellow]🔍 Checking & Installing Required Libraries...[/bold yellow]\n")
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        transient=True,
    ) as progress:
        for lib in REQUIRED_LIBS:
            task = progress.add_task(f"[blue]Checking {lib}...", start=True)
            time.sleep(1)
            try:
                __import__(lib)
                progress.update(task, description=f"[green]✔ {lib} already installed")
            except ImportError:
                progress.update(task, description=f"[yellow]➕ Installing {lib}...")
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", lib], stdout=subprocess.DEVNULL)
                    progress.update(task, description=f"[green]✅ Installed {lib}")
                except subprocess.CalledProcessError:
                    progress.update(task, description=f"[red]❌ Failed to install {lib}")
                    console.print(f"[red]❗ Error installing {lib}. Exiting...[/red]")
                    sys.exit(1)
            time.sleep(1)


# 📁 Create files
def create_project_files():
    console.print("\n[bold green]📁 Creating Your Project Files...[/bold green]")
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
        transient=True,
    ) as progress:
        task1 = progress.add_task("Writing app.py...", total=100)
        time.sleep(1)
        with open("app.py", "w") as f:
            f.write(TEMPLATE_APP)
        progress.update(task1, advance=100)
        time.sleep(1)

        task2 = progress.add_task("Writing templates.html...", total=100)
        with open("templates.html", "w", encoding="utf-8") as f:
            f.write(TEMPLATE_HTML)
        progress.update(task2, advance=100)
        time.sleep(1)


# 🌳 Tree + Congrats
def show_success_tree():
    tree = Tree("📂 [bold blue]Project Structure[/bold blue]")
    tree.add("app.py")
    tree.add("templates.html")

    congrats = Panel.fit(
        "[bold green]🎉 Congratulations! Your FeniX project is ready to fly![/bold green]\n"
        "🔥 Build something legendary...\n"
        "🚀 Run with [bold yellow]fx server[/bold yellow] or customize your magic ✨",
        title="✅ [bold cyan]Setup Complete[/bold cyan]",
        border_style="bright_magenta",
    )
    console.print(tree)
    console.print(congrats)


# 🚀 Final create method
def create():
    if Path("app.py").exists() or Path("templates.html").exists():
        console.print("[bold red]⚠ Project already exists in this folder![/bold red]")
        return

    show_banner()
    install_requirements()
    create_project_files()
    show_success_tree()
