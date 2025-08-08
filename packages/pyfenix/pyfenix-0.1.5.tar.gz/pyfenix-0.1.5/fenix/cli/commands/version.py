import time
from rich.console import Console
from rich.panel import Panel
from fenix import __version__

console = Console()

def typing(text: str, delay: float = 0.02, style="bold green"):
    for char in text:
        console.print(char, end="", style=style, soft_wrap=True)
        time.sleep(delay)
    print()

def show():
    # Cool banner
    panel = Panel.fit(
        "[bold cyan]🧿 Powered by FeniX[/bold cyan]\n✨ Crafting Future Webs",
        border_style="magenta"
    )
    console.print(panel)
    time.sleep(0.5)

    # Typing effect
    typing(f"📦 Framework Version → v{__version__}", 0.03, "bold green")
    time.sleep(0.2)
    typing("🚀 Built for speed, crafted with ❤️", 0.025, "yellow")
