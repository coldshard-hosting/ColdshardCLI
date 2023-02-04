import click
import pathlib
import json

from .utils import request

@click.group()
def core():
    """The ColdShard CLI. For more information, use the help command."""
    if not pathlib.Path("../config.json").exists():
        with open("../config.json", "w") as f:
            f.write("{}")
    click.echo(click.style("Welcome to the ColdShard CLI!", fg="green", bold=True)) 

@core.command()
@click.option("--api-key", prompt="API Key", hide_input=True)
def login(api_key: str):
    """Login to the panel using your API Key"""

    response = request("GET", "account", api_key=api_key)

    if not response:
        return # The request was not made because there was no API key.

    data = response.json()
    account = data["attributes"]

    with open("../config.json", "w") as f:
        json.dump({"api_key": api_key}, f, indent=4)
    click.echo(click.style(f"Successfully logged in as {account['email']}", fg="green", bold=True))

@core.command()
def logout():
    """Logout of the panel."""
    with open("../config.json", "w") as f:
        json.dump({}, f, indent=4)
    click.echo(click.style("Successfully logged out", fg="green", bold=True))

@core.command("account")
def account():
    """Get information about your account."""
    response = request("GET", "account")

    if not response:
        return

    data = response.json()
    account = data["attributes"]

    info: str = ""

    info += click.style(f"Email: {account['email']}\n", fg="blue", bold=True)
    info += click.style(f"Username: {account['username']}\n", fg="blue", bold=True)

    click.echo(info)