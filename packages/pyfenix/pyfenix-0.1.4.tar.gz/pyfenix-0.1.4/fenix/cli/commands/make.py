# fenix/cli/commands/make.py

import time
from pathlib import Path
from rich.console import Console
from rich.progress import Progress
from rich.tree import Tree

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

def create():
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

    tree = Tree("📂 [bold blue]Project Structure[/bold blue]")
    tree.add("app.py")
    tree.add("templates.html")
    console.print(tree)
