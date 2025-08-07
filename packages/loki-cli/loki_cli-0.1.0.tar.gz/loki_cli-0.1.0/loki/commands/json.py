#!/usr/bin/env python3

"""JSON command module for Loki CLI"""

import sys
import json as json_lib
import typer
from typing import Optional

app = typer.Typer(help="JSON formatting operations")


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
    json_data: Optional[str] = typer.Argument(None, help="JSON data to format"),
    infile: Optional[str] = typer.Option(None, "--infile", "-i", help="Input file path"),
    outfile: Optional[str] = typer.Option(None, "--outfile", "-o", help="Output file path"),
    indent: int = typer.Option(2, "--indent", "-n", help="Indentation level"),
):
    """Pretty-prints a JSON string or file"""
    try:
        # Read input
        input_data = read_input(json_data, infile)
        if not input_data:
            typer.echo("Error: No input provided", err=True)
            raise typer.Exit(code=1)
        
        # Parse and format JSON
        parsed_json = json_lib.loads(input_data)
        formatted_json = json_lib.dumps(parsed_json, indent=indent)
        
        # Write output
        write_output(formatted_json, outfile)
        
    except Exception as e:
        typer.echo(f"Error formatting JSON: {str(e)}", err=True)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
