# fastbuild/fastbuild/cli.py

from subprocess import run
import click
from .commands import init_project, run_app, add_db, remove_db
from .version import get_version

@click.group(
    help="CLI para criação rápida de projetos FastAPI.",
    invoke_without_command=True
)
@click.version_option(get_version(), "-v", "--version", message="fastbuild versão %(version)s")
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())

cli.add_command(init_project)
cli.add_command(run_app)
cli.add_command(add_db) 
cli.add_command(remove_db)

if __name__ == "__main__":
    cli()
