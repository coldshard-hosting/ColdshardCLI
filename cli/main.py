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

@core.command()
@click.option("--api-key", prompt="API Key", hide_input=True)
def login(api_key: str):
    """Login to the panel using your API Key"""

    response = request("GET", "/account", api_key=api_key)

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
    response = request("GET", "/account")

    if not response:
        return

    data = response.json()
    account = data["attributes"]

    info: str = ""

    info += click.style(f"Email: {account['email']}\n", bold=True)
    info += click.style(f"Username: {account['username']}\n", bold=True)

    click.echo(info)

@core.group("servers")
def servers():
    """Commands related to servers."""
    ...

@servers.command("list")
@click.option("--mine", is_flag=True, help="Only list your servers.")
@click.option("--hide-suspended", is_flag=True, help="Hide suspended servers.")
@click.option("--count", default=10, help="The amount of servers to list.", type=int)
def list_servers(mine: bool, hide_suspended, count: int):
    """List your servers."""

    response = request("GET", "/")
    
    if not response:
        return

    data = response.json()
    servers = data["data"]

    message = ""

    for index, _server in enumerate(servers):
        server = _server["attributes"]

        if mine and not server["server_owner"]:
            continue

        if hide_suspended and server["is_suspended"]:
            continue
        if index + 1 >= count:
            break

        message += click.style(f"Name: {server['name']}", bold=True)
        message += "\n"
    
    click.echo(message)

@servers.command("view")
@click.option("--id", help="The ID of the server to view.", prompt="Server ID: ")
def view_server(id: str):
    """View information about a specific server."""
    
    response = request("GET", f"/servers/{id}")

    if not response:
        return
    
    data = response.json()

    