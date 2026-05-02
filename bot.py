import typer
from src.targets import add_target, remove_target, load_targets
from src.checker import check_all
from src.telegram import send_test_message
from src.scheduler import start_scheduler

app = typer.Typer()

@app.command()
def add(
    url: str = typer.Option(..., help="URL to monitor"),
    target: float = typer.Option(..., help="Target price to alert at"),
    label: str = typer.Option("", help="Optional label for this target")
):
    """Add a URL to monitor."""
    add_target(url, target, label)

@app.command()
def remove(
    url: str = typer.Option(..., help="URL to remove")
):
    """Remove a monitored URL."""
    remove_target(url)

@app.command()
def list():
    """List all monitored URLs."""
    targets = load_targets()
    if not targets:
        typer.echo("No targets yet. Use 'add' to add one.")
        return
    for t in targets:
        status = "active" if t.get("active", True) else "paused"
        typer.echo(f"- {t['label']} | Target: {t['target_price']} | Last price: {t.get('last_price', 'not checked yet')} | {status}")

@app.command()
def check():
    """Check all URLs once and send alerts if price is hit."""
    check_all()

@app.command()
def start():
    """Start the scheduler to check automatically."""
    start_scheduler()

@app.command()
def test():
    """Send a test message to Telegram."""
    send_test_message()

if __name__ == "__main__":
    app()
