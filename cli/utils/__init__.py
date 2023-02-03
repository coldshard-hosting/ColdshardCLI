from typing import Optional
import click
import requests
import json

PANEL_API_URL: str = "https://panel.coldshard.com/api/client"

def is_logged_in() -> bool:
    """Check if the user is logged in."""
    with open("../config.json", "r") as f:
        config = json.load(f)
    if config.get("api_key"):
        return True
    return False

def get_api_key() -> Optional[str]:
    """Get the API Key from the config file."""
    logged_in = is_logged_in()
    if not logged_in:
        return None
    with open("../config.json", "r") as f:
        config = json.load(f)
    return config["api_key"]

def warn_not_logged_in() -> None:
    click.echo(click.style("You are not logged in.", fg="red", bold=True))


def request(method: str, endpoint: str, **kwargs) -> Optional[requests.Response]:
    """Make a request to the panel."""
    api_key: Optional[str] = get_api_key()

    if not api_key:
        warn_not_logged_in()
        return

    response = requests.request(
        method, f"{PANEL_API_URL}/{endpoint}", headers={"Authorization": f"Bearer {api_key}"}, **kwargs
    )

    return response