import click
import logging
import sys
from pathlib import Path
from .server import main as server_main

@click.command()
@click.option("-v", "--verbose", count=True)
def main(verbose: int) -> None:
    """SAST Fixer MCP Server - SAST vulnerability fixing service for MCP"""
    logging_level = logging.WARN
    if verbose == 1:
        logging_level = logging.INFO
    elif verbose >= 2:
        logging_level = logging.DEBUG

    logging.basicConfig(level=logging_level, stream=sys.stderr)
    server_main()

if __name__ == "__main__":
    main()