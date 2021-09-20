"""Commands related to the servers."""
import click

# from ..server import start_server


@click.group()
def server() -> None:
    """Server commands"""  # noqa: D400
    pass
