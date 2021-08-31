import click

from ..server import start_server


@click.command()
@click.pass_context
def server(ctx):
    start_server(ctx.obj['config'])
