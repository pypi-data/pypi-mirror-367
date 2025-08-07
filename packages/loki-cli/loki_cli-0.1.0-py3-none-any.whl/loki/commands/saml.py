#!/usr/bin/env python3

"""SAML command module for Loki CLI"""

import sys
import base64
import typer
from typing import Optional
from lxml import etree

app = typer.Typer(help="SAML response decoding operations")


def read_input(data: Optional[str], infile: Optional[str]) -> str:
    """Read input from string, file, or stdin"""
    if data:
        return data
    elif infile:
        with open(infile, 'r') as f:
            return f.read().strip()
    else:
        return sys.stdin.read().strip()


def write_output(content: str, outfile: Optional[str]) -> None:
    """Write output to file or stdout"""
    if outfile:
        with open(outfile, 'w') as f:
            f.write(content)
    else:
        typer.echo(content)


@app.command()
def decode(
    saml_response: Optional[str] = typer.Argument(None, help="Base64-encoded SAML response"),
    infile: Optional[str] = typer.Option(None, "--infile", "-i", help="Input file path"),
    outfile: Optional[str] = typer.Option(None, "--outfile", "-o", help="Output file path"),
):
    """Decode a Base64-encoded SAML Response into readable XML"""
    try:
        # Read input
        input_data = read_input(saml_response, infile)
        if not input_data:
            typer.echo("Error: No input provided", err=True)
            raise typer.Exit(code=1)
        
        # Decode Base64
        decoded_bytes = base64.b64decode(input_data)
        decoded_string = decoded_bytes.decode('utf-8')
        
        # Parse and pretty print XML
        root = etree.fromstring(decoded_string)
        pretty_xml = etree.tostring(root, pretty_print=True, encoding='unicode')
        
        # Write output
        write_output(pretty_xml, outfile)
        
    except Exception as e:
        typer.echo(f"Error decoding SAML: {str(e)}", err=True)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
