from typing import Optional
import click
import requests
import json

PANEL_API_URL: str = "https://panel.coldshard.com/api/client"

def is_logged_in() -> bool:
    """Check if the user is logged in."""
    try:
        with open("../config.json", "rb", ) as f:
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

def request(method: str, endpoint: str, *, api_key: Optional[str] = None, **kwargs) -> Optional[requests.Response]:
    """Make a request to the panel."""

    if not api_key:

        if not is_logged_in():
            warn_not_logged_in()
            return

        api_key = get_api_key()

    response = requests.request(
        method, f"{PANEL_API_URL}/{endpoint}", headers={"Authorization": f"Bearer {api_key}"}, **kwargs
    )

    return response