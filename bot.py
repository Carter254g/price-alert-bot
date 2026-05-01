import typer
app = typer.Typer()

@app.command()
def add(url: str = typer.Option(..., help="URL to monitor"),
        target: float = typer.Option(..., help="Target price to alert at")):
    """Add a URL to monitor."""
    typer.echo(f"Added: {url} with target price {target}")

@app.command()
def list():
    """List all monitored URLs."""
    typer.echo("No targets yet. Use 'add' to add one.")

@app.command()
def check():
    """Check all URLs once."""
    typer.echo("Checking all targets...")

@app.command()
def start():
    """Start the scheduler."""
    typer.echo("Starting scheduler...")

if __name__ == "__main__":
    app()
