#!/usr/bin/env python3

"""XML command module for Loki CLI"""

import sys
import typer
from typing import Optional
from lxml import etree

app = typer.Typer(help="XML formatting operations")


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
def format(
    xml_data: Optional[str] = typer.Argument(None, help="XML data to format"),
    infile: Optional[str] = typer.Option(None, "--infile", "-i", help="Input file path"),
    outfile: Optional[str] = typer.Option(None, "--outfile", "-o", help="Output file path"),
):
    """Pretty-prints an XML string or file"""
    try:
        # Read input
        input_data = read_input(xml_data, infile)
        if not input_data:
            typer.echo("Error: No input provided", err=True)
            raise typer.Exit(code=1)
        
        # Parse and format XML
        root = etree.fromstring(input_data)
        formatted_xml = etree.tostring(root, pretty_print=True, encoding='unicode')
        
        # Write output
        write_output(formatted_xml, outfile)
        
    except Exception as e:
        typer.echo(f"Error formatting XML: {str(e)}", err=True)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
