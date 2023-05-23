import inquirer
from typing import Optional
import click
import pytero
import json

PANEL_API_URL: str = "https://panel.coldshard.com/api/client"


def is_logged_in() -> bool:
    """Check if the user is logged in."""
    try:
        with open(
            "../config.json",
            "r",
        ) as f:
            config = json.load(f)

        if not config.get("api_key"):
            return False
        return True
    except FileNotFoundError:
        return False


def get_api_key() -> str:
    """Get the API Key from the config file."""
    with open("../config.json", "r") as f:
        config = json.load(f)

    return config["api_key"]


def warn_not_logged_in() -> None:
    click.echo(click.style("You are not logged in.", fg="red", bold=True))



async def prompt_server() -> Optional[pytero.ClientServer]:
    """Prompt the user to select a server."""
    if not is_logged_in():
        warn_not_logged_in()
        return None
    
    api_key = get_api_key()
    client = pytero.PteroClient(PANEL_API_URL, api_key)
    servers = await client.get_servers()

    server_names = {
        server.name: server
        for server in servers
    }

    questions = [
        inquirer.List("server", message="Select a server", choices=server_names.keys())
    ]

    try:
        answers = inquirer.prompt(questions, raise_keyboard_interrupt=True)
    except KeyboardInterrupt:
        click.echo(click.style("Cancelled.", fg="red", bold=True))
        exit(1)

    server = server_names[answers["server"]] # type: ignore

    return server
