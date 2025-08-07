from rich.console import Console
from typer import Typer

app = Typer()
console = Console()


@app.command()
def model(name: str):
    console.print(f"\nCreating new model: {name}")
