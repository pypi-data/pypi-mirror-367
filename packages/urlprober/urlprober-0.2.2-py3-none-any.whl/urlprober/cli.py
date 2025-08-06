"""Provide command line interface for URL Prober."""

import click

from urlprober.app import create_app


@click.group()
def cli():
    """Define URL Prober CLI group."""
    pass


@cli.command()
@click.option("--host", default="127.0.0.1", help="Host to bind to")
@click.option("--port", default=8080, help="Port to bind to")
@click.option("--debug", is_flag=True, help="Enable debug mode")
def serve(host: str, port: int, debug: bool):
    """Start the Flask server."""
    app = create_app()
    app.run(host=host, port=port, debug=debug)


def main():
    """Execute the main CLI program."""
    cli()


if __name__ == "__main__":
    main()
