import click
import requests
import pathlib
import json

PANEL_API_URL: str = "https://panel.coldshard.com/api/client"

@click.group()
def core():
    """The ColdShard CLI. For more information, use the help command."""
    if not pathlib.Path("config.json").exists():
        with open("config.json", "w") as f:
            f.write("{}")

@core.command()
@click.argument("api_key")
def login(api_key: str):
    """Login to the panel using your API Key"""
    response = requests.get(f"{PANEL_API_URL}/account")
    if not response.ok:

        click.echo(click.style("Invalid API Key", fg="red", bold=True))
        return
    with open("config.json", "w") as f:
        json.dump({"api_key": api_key}, f, indent=4)
    click.echo(click.style("Successfully logged in", fg="green", bold=True))

if __name__ == "__main__":
    core()