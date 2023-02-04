import click
import pathlib
import json
import inquirer

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
def view_server():
    """View information about a specific server."""

    servers_response = request("GET", "/")

    if not servers_response:
        return
    
    data = servers_response.json()
    servers = data["data"]

    server_names = {server["attributes"]["name"]: server["attributes"]["identifier"] for server in servers}

    questions = [
        inquirer.List("server", message="Select a server", choices=server_names.keys())
    ]

    answer = inquirer.prompt(questions)

    id = server_names[answer["server"]] # type: ignore


    server_response = request("GET", f"/servers/{id}")

    if not server_response:
        return
    
    data = server_response.json()

    server = data["attributes"]

    stats_response = request("GET", f"/servers/{id}/resources")

    if not stats_response:
        return
    
    _stats = stats_response.json()
    current_state = _stats["attributes"]["current_state"]
    stats = _stats["attributes"]["resources"]

    message = ""

    message += click.style(f"Name:                     {server['name']}", bold=True)
    message += "\n"
    message += click.style(f"Current status:           {current_state.title()}", bold=True)
    message += "\n"
    message += click.style(f"Owner:                    {server['server_owner']}", bold=True)
    message += "\n"
    message += click.style(f"CPU Usage:                {stats['cpu_absolute']}/{server['limits']['cpu'] or '-'}%", bold=True)
    message += "\n"
    message += click.style(f"RAM Usage:                {round(stats['memory_bytes'] / 1024 / 1024)}/{server['limits']['memory'] or '-'}MB", bold=True)
    message += "\n"
    message += click.style(f"Disk Usage:               {round(stats['disk_bytes'] / 1024 / 1024)}/{server['limits']['disk'] or '-'}MB", bold=True)
    message += "\n"
    message += click.style(f"Network Usage (Inbound):  {round(stats['network_rx_bytes'] / 1024 / 1024)}MB", bold=True)
    message += "\n"
    message += click.style(f"Network Usage (Outbound): {round(stats['network_tx_bytes'] / 1024 / 1024)}MB", bold=True)
    message += "\n"

    click.echo(message)