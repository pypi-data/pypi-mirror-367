import json
import re
import sys

import click
import yumako
from hcs_core.sglib import cli_options as cli

from hcs_cli.service import VM, hoc
from hcs_cli.support import predefined_payload


@click.command()
@cli.org_id
@click.option(
    "--from",
    "from_param",
    type=str,
    required=False,
    default="-12h",
    help="Sepcify the from date. E.g. '-1d', or '-1h35m', or '-1w', or '2023-12-04T00:19:22.854Z'.",
)
@click.option(
    "--to",
    type=str,
    required=False,
    default="now",
    help="Sepcify the to date. E.g. 'now', or '-1d', or '-1h35m', or '-1w', or '2023-12-04T00:19:22.854Z'.",
)
def connect(org: str, from_param: str, to: str):
    """Analyse connect issue."""
    pass
