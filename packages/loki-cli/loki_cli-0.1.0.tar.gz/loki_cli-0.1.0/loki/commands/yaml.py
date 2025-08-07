#!/usr/bin/env python3

"""YAML command module for Loki CLI"""

import sys
import yaml as yaml_lib
import typer
from typing import Optional

app = typer.Typer(help="YAML formatting operations")


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
    yaml_data: Optional[str] = typer.Argument(None, help="YAML data to format"),
    infile: Optional[str] = typer.Option(None, "--infile", "-i", help="Input file path"),
    outfile: Optional[str] = typer.Option(None, "--outfile", "-o", help="Output file path"),
):
    """Pretty-prints a YAML string or file"""
    try:
        # Read input
        input_data = read_input(yaml_data, infile)
        if not input_data:
            typer.echo("Error: No input provided", err=True)
            raise typer.Exit(code=1)
        
        # Parse and format YAML
        parsed_yaml = yaml_lib.safe_load(input_data)
        formatted_yaml = yaml_lib.dump(parsed_yaml, default_flow_style=False, indent=2)
        
        # Write output
        write_output(formatted_yaml, outfile)
        
    except Exception as e:
        typer.echo(f"Error formatting YAML: {str(e)}", err=True)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
