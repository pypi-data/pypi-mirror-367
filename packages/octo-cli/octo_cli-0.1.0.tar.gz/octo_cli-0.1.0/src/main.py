import typer
from typer import Typer

app = Typer()


@app.callback()
def callback():
    pass


@app.command()
def shoot():
    typer.echo("Shooting portal gun")
