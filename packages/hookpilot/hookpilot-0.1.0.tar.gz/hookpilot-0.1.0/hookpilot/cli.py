import typer

app = typer.Typer(help="Hookpilot - A lightweight Git hook manager in Python")

@app.command()
def install():
    "Install Git hooks into the current repository"
    typer.echo("Installing Git hooks...")

@app.command()
def run(hook:str):
    "Run a specific Git hook"
    typer.echo(f"Running {hook} hook...")

if __name__ == "__main__":
    app()