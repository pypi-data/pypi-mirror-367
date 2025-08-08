import time
from rich.console import Console
from rich.panel import Panel

console = Console()


def typing(text: str, delay: float = 0.02):
    for char in text:
        console.print(char, end="", style="bold cyan", soft_wrap=True)
        time.sleep(delay)
    print()


def run():
    banner = Panel.fit(
        "[bold magenta]✨ Welcome to the FeniX CLI[/bold magenta]\n🔥 Let's build something legendary!",
        border_style="bright_yellow",
    )

    console.print(banner)
    time.sleep(0.3)

    typing("\n🛠️ Available Commands in FeniX CLI:\n", 0.03)

    time.sleep(0.2)
    typing("  📦 version         → Show framework version", 0.01)
    typing("  🚀 make project    → Create a new FeniX project", 0.01)
    typing("  🖥️  server          → Run development server", 0.01)
    typing("  📘 help            → Show this help message\n", 0.01)

    time.sleep(0.4)
    typing("💡 Usage Examples:\n", 0.03)
    typing("  🧪 tfx version", 0.01)
    typing("  🛠️  tfx make project", 0.01)
    typing("  🔄 tfx server", 0.01)
    typing("  🆘 tfx help", 0.01)

    console.print("\n[bold green]✨ Tip:[/bold green] Use [yellow]tfx make project[/yellow] to start building magic! 🪄\n")
