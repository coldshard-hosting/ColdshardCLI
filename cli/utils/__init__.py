import inquirer
from typing import Optional, Any
import click
import requests
import json

PANEL_API_URL: str = "https://panel.coldshard.com/api/client"


def is_logged_in() -> bool:
    """Check if the user is logged in."""
    try:
        with open(
            "../config.json",
            "rb",
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


def request(
    method: str, endpoint: str, *, api_key: Optional[str] = None, **kwargs
) -> Optional[requests.Response]:
    """Make a request to the panel."""

    if not api_key:

        if not is_logged_in():
            warn_not_logged_in()
            return

        api_key = get_api_key()

    response = requests.request(
        method,
        f"{PANEL_API_URL}{endpoint}",
        headers={"Authorization": f"Bearer {api_key}"},
        **kwargs,
    )

    if response.status_code == 401:
        click.echo(click.style("Invalid API Key.", fg="red", bold=True))
        return

    if response.status_code == 403:
        click.echo(
            click.style(
                "You do not have permission to perform this action.",
                fg="red",
                bold=True,
            )
        )
        return

    if response.status_code == 404:
        click.echo(
            click.style(
                f"The requested resource ({PANEL_API_URL}{endpoint}) was not found.",
                fg="red",
                bold=True,
            )
        )
        return

    if response.status_code == 429:
        click.echo(click.style("You have been ratelimited.", fg="red", bold=True))
        return

    if response.status_code == 500:
        click.echo(
            click.style(
                "An internal server error occurred. Our servers may be down.",
                fg="red",
                bold=True,
            )
        )
        return

    return response


def prompt_server() -> Optional[tuple[dict[Any, Any], Optional[dict[Any, Any]]]]:

    servers_response = request("GET", "/")

    if not servers_response:
        return

    data = servers_response.json()
    servers = data["data"]

    server_names = {
        server["attributes"]["name"]: server["attributes"]["identifier"]
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

    return (server_names, answers)
