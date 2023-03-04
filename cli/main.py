import click
import pathlib
import json

from .utils import request, prompt_server

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

    results = prompt_server()

    if not results:
        return
    
    server_names, answer = results

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

@servers.command("start")
def start_server():
    """Start a server."""

    results = prompt_server()

    if not results:
        return

    

    server_names, answer = results

    id = server_names[answer["server"]] # type: ignore

    stats_response = request("GET", f"/servers/{id}/resources")

    if not stats_response:
        return
    
    _stats = stats_response.json()
    current_state = _stats["attributes"]["current_state"]

    if current_state in ("running", "starting"):
        click.echo(click.style("This server is already running.", fg="red", bold=True))
        return

    response = request("POST", f"/servers/{id}/power", json={"signal": "start"}) # type: ignore

    if not response:
        return
    
    click.echo(click.style("Successfully started server.", fg="green", bold=True))

@servers.command("stop")
def stop_server():
    """Stop a server."""

    results = prompt_server()

    if not results:
        return

    server_names, answer = results

    id = server_names[answer["server"]] # type: ignore

    stats_response = request("GET", f"/servers/{id}/resources")

    if not stats_response:
        return
    
    _stats = stats_response.json()
    current_state = _stats["attributes"]["current_state"]


    if current_state in ("stopped", "stopping"):
        click.echo(click.style("This server is already stopped.", fg="red", bold=True))
        return
    
    response = request("POST", f"/servers/{id}/power", json={"signal": "stop"})

    if not response:
        return
    
    click.echo(click.style("Successfully stopped server.", fg="green", bold=True))

@servers.command("restart")
def restart_server():
    """Restart a server."""

    results = prompt_server()

    if not results:
        return

    

    server_names, answer = results

    id = server_names[answer["server"]] # type: ignore

    response = request("POST", f"/servers/{id}/power", json={"signal": "restart"})

    if not response:
        return
    
    click.echo(click.style("Successfully restarted server.", fg="green", bold=True))

@servers.command("kill")
def kill_server():
    """Kill a server."""

    results = prompt_server()

    if not results:
        return

    server_names, answer = results

    id = server_names[answer["server"]] # type: ignore

    response = request("POST", f"/servers/{id}/power", json={"signal": "kill"})

    if not response:
        return

    click.echo(click.style("Successfully killed server.", fg="green", bold=True))
