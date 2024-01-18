import logging

import click
import pytest
from flask.cli import with_appcontext

logging.getLogger("faker").setLevel(logging.INFO)


@click.command("test")
@with_appcontext
def run_pytest():
    pytest.main(["-s", "tests"])
