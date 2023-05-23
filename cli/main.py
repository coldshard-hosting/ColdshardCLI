#!/usr/bin/env python
import json
import pathlib

import asyncclick as click
import pytero

from .utils import prompt_server, is_logged_in, get_api_key, warn_not_logged_in, PANEL_API_URL


@click.group()
async def core():
    """The ColdShard CLI. For more information, use the help command."""
    if not pathlib.Path("../config.json").exists():
        with open("../config.json", "w") as f:
            f.write("{}")


@core.command()
@click.option("--api-key", prompt="API Key", hide_input=True)
async def login(api_key: str):
    """Login to the panel using your API Key"""
    client = pytero.PteroClient(PANEL_API_URL, api_key)
    account = await client.get_account()
    
    with open("../config.json", "w") as f:
        json.dump({"api_key": api_key}, f, indent=4)
    click.echo(
        click.style(
            f"Successfully logged in as {account.email}", fg="green", bold=True
        )
    )


@core.command()
async def logout():
    """Logout of the panel."""
    with open("../config.json", "w") as f:
        json.dump({}, f, indent=4)
    click.echo(click.style("Successfully logged out", fg="green", bold=True))


@core.command("account")
async def account():
    """Get information about your account."""
    if not is_logged_in():
        warn_not_logged_in()
        return
    
    api_key = get_api_key()
    client = pytero.PteroClient(PANEL_API_URL, api_key)
    account = await client.get_account()
    info: str = ""

    info += click.style(f"Email: {account.email}\n", bold=True)
    info += click.style(f"Username: {account.username}\n", bold=True)

    click.echo(info)


@core.group("servers")
async def servers():
    """Commands related to servers."""
    ...


@servers.command("list")
@click.option("--mine", is_flag=True, help="Only list your servers.")
@click.option("--hide-suspended", is_flag=True, help="Hide suspended servers.")
@click.option("--count", default=10, help="The amount of servers to list.", type=int)
async def list_servers(mine: bool, hide_suspended, count: int):
    """List your servers."""

    if not is_logged_in():
        warn_not_logged_in()
        return
    
    api_key = get_api_key()
    client = pytero.PteroClient(PANEL_API_URL, api_key)
    servers = await client.get_servers()

    message = ""

    for index, server in enumerate(servers):

        if mine and not server.server_owner:
            continue

        if hide_suspended and server.is_suspended:
            continue

        if index + 1 >= count:
            break

        message += click.style(f"Name: {server.name}", bold=True)
        message += "\n"

    click.echo(message)


@servers.command("view")
async def view_server():
    """View information about a specific server."""
    if not is_logged_in():
        warn_not_logged_in()
        return
    
    api_key = get_api_key()
    client = pytero.PteroClient(PANEL_API_URL, api_key)

    server = await prompt_server()

    if not server:
        return

    stats = await client.get_server_resources(server.identifier)

    current_state = stats.current_state
    stats = stats.resources

    message = ""

    message += click.style(f"Name:                     {server.name}", bold=True)
    message += "\n"
    message += click.style(
        f"Current status:           {current_state.title()}", bold=True
    )
    message += "\n"
    message += click.style(
        f"Owner:                    {server.server_owner}", bold=True
    )
    message += "\n"
    message += click.style(
        "CPU Usage:                "
        f"{stats.cpu_absolute}/{server.limits.cpu or '-'}%",
        bold=True,
    )
    message += "\n"
    message += click.style(
        "RAM Usage:                "
        f"{round(stats.memory_bytes / 1024 / 1024)}/{server.limits.memory or '-'}MB",  # noqa: E501
        bold=True,
    )
    message += "\n"
    message += click.style(
        "Disk Usage:               "
        f"{round(stats.disk_bytes / 1024 / 1024)}/{server.limits.disk or '-'}MB",  # noqa: E501
        bold=True,
    )
    message += "\n"
    message += click.style(
        f"Network Usage (Inbound):  {round(stats.network_rx_bytes / 1024 / 1024)}MB",
        bold=True,
    )
    message += "\n"
    message += click.style(
        f"Network Usage (Outbound): {round(stats.network_tx_bytes / 1024 / 1024)}MB",
        bold=True,
    )
    message += "\n"

    click.echo(message)


@servers.command("start")
async def start_server():
    """Start a server."""
    if not is_logged_in():
        warn_not_logged_in()
        return

    api_key = get_api_key()
    client = pytero.PteroClient(PANEL_API_URL, api_key)

    server = await prompt_server()

    if not server:
        return

    stats = await client.get_server_resources(server.identifier)
    current_state = stats.current_state

    if current_state in ("running", "starting"):
        click.echo(click.style("This server is already running.", fg="red", bold=True))
        return

    await client.send_server_power(server.identifier, "start")

    click.echo(click.style("Successfully started server.", fg="green", bold=True))


@servers.command("stop")
async def stop_server():
    """Stop a server."""
    if not is_logged_in():
        warn_not_logged_in()
        return
    
    api_key = get_api_key()
    client = pytero.PteroClient(PANEL_API_URL, api_key)

    server = await prompt_server()

    if not server:
        return

    stats = await client.get_server_resources(server.identifier)

    current_state = stats.current_state

    if current_state in ("stopped", "stopping"):
        click.echo(click.style("This server is already stopped.", fg="red", bold=True))
        return

    await client.send_server_power(server.identifier, "stop")

    click.echo(click.style("Successfully stopped server.", fg="green", bold=True))


@servers.command("restart")
async def restart_server():
    """Restart a server."""
    if not is_logged_in():
        warn_not_logged_in()
        return
    
    api_key = get_api_key()
    client = pytero.PteroClient(PANEL_API_URL, api_key)

    server = await prompt_server()

    if not server:
        return

    await client.send_server_power(server.identifier, "restart")

    click.echo(click.style("Successfully restarted server.", fg="green", bold=True))


@servers.command("kill")
async def kill_server():
    """Kill the power on a server."""
    if not is_logged_in():
        warn_not_logged_in()
        return
    
    api_key = get_api_key()
    client = pytero.PteroClient(PANEL_API_URL, api_key)

    server = await prompt_server()

    if not server:
        return

    await client.send_server_power(server.identifier, "kill")

    click.echo(click.style("Successfully killed server.", fg="green", bold=True))
