import subprocess
import sys
import time
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

console = Console()

def typing(text: str, delay: float = 0.02, style="bold cyan"):
    for char in text:
        console.print(char, end="", style=style, soft_wrap=True)
        time.sleep(delay)
    print()

def dev_server():
    if not Path("app.py").exists():
        typing("❌ Oh no! 'app.py' not found in current directory. Please create a project first.\n", 0.03, "bold red")
        return

    # Show intro panel
    banner = Panel.fit(
        "[bold magenta]🧿 FeniX Dev Mode[/bold magenta]\n💻 Booting up your server with magic...",
        border_style="bright_yellow"
    )
    console.print(banner)
    time.sleep(0.5)

    # Typing effect while booting
    typing("🔍 Checking dependencies...", 0.03)
    time.sleep(0.3)
    typing("⚙️ Spinning up the core engine...", 0.03)
    time.sleep(0.4)
    typing("🛡️ Loading routes and templates...", 0.03)
    time.sleep(0.5)
    typing("🚀 Launching FeniX server now...\n", 0.03, "bold green")
    time.sleep(0.5)

    # Actually run the server
    subprocess.run([sys.executable, "app.py"])
