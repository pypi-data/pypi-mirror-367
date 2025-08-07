#!/usr/bin/env python3

"""Loki CLI - Offline Developer Toolkit"""

import typer

from loki.commands import jwt, saml, json, xml, yaml, csv

app = typer.Typer(
    help="Loki CLI - Offline Developer Toolkit for data transformation, formatting, and token decoding",
    no_args_is_help=True,
    pretty_exceptions_show_locals=False,
)

# Register subcommands
app.add_typer(jwt.app, name="jwt")
app.add_typer(saml.app, name="saml")
app.add_typer(json.app, name="json")
app.add_typer(xml.app, name="xml")
app.add_typer(yaml.app, name="yaml")
app.add_typer(csv.app, name="csv")

if __name__ == "__main__":
    app()
