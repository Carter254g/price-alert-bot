import typer
from src.targets import add_target, remove_target, load_targets, pause_target, resume_target
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
def pause(
    url: str = typer.Option(..., help="URL to pause")
):
    """Pause monitoring a URL."""
    pause_target(url)

@app.command()
def resume(
    url: str = typer.Option(..., help="URL to resume")
):
    """Resume monitoring a paused URL."""
    resume_target(url)

@app.command()
def list():
    """List all monitored URLs."""
    targets = load_targets()
    if not targets:
        typer.echo("No targets yet. Use 'add' to add one.")
        return
    typer.echo(f"\n{'Label':<30} {'Target':>10} {'Last Price':>12} {'Status':<10}")
    typer.echo("-" * 65)
    for t in targets:
        status = "active" if t.get("active", True) else "paused"
        last = str(t.get("last_price") or "not checked")
        typer.echo(f"{t['label']:<30} {t['target_price']:>10} {last:>12} {status:<10}")

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
