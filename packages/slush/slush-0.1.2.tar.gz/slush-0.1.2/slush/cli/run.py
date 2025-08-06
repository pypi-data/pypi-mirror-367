import os, sys
import click
from slush.server import run
from importlib import import_module
from importlib.metadata import version, PackageNotFoundError

sys.path.insert(0, os.getcwd())


def get_version():
    try:
        return version("slush")
    except PackageNotFoundError:
        return "unknown"
    
@click.group()
@click.version_option(get_version(), "-v", "--version", message="Slush version: %(version)s")
@click.help_option("--help", "-h")
def cli():
    """🧊 Slush CLI"""
    pass

@cli.command()
@click.argument('app_path')
@click.option('--host', default='127.0.0.1', help='Host to bind the server to')
@click.option('--port', default=8000, type=int, help='Port to run the server on')
@click.option('--reload', default=True, is_flag=True, help='Enable auto-reloading of the server')
def runserver(app_path, host, port, reload):
    """Start your Slush app (example: slush runserver example:app)"""
    if ":" not in app_path:
        raise click.UsageError("⚠️ Please provide app in format module:app (e.g. example:app)")

    module_name, app_name = app_path.split(":")
    try:
        mod = import_module(module_name)
        app = getattr(mod, app_name)
    except (ImportError, AttributeError) as e:
        raise click.ClickException(f"❌ Failed to import app: {e}")

    click.secho(f"🧊 Starting Slush app [{module_name}.{app_name}] at http://{host}:{port}", fg='green')
    run(app, host=host, port=port, reload=reload)



