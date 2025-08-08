# fenix/cli/commands/run.py

import subprocess
import sys
from pathlib import Path
from rich.console import Console

console = Console()

def dev_server():
    if not Path("app.py").exists():
        console.print("[bold red]❌ app.py not found in current directory![/bold red]")
        return

    console.print("[bold yellow]🚀 Starting FeniX server...[/bold yellow]")
    subprocess.run([sys.executable, "app.py"])
