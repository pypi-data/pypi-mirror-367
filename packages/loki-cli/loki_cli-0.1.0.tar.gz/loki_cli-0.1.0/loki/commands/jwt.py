#!/usr/bin/env python3

"""JWT command module for Loki CLI"""

import sys
import typer
import jwt as pyjwt
from typing import Optional

app = typer.Typer(help="JWT token decoding operations")


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
    token: Optional[str] = typer.Argument(None, help="JWT token to decode"),
    infile: Optional[str] = typer.Option(None, "--infile", "-i", help="Input file path"),
    outfile: Optional[str] = typer.Option(None, "--outfile", "-o", help="Output file path"),
):
    """Decode a JWT token to display its header and payload"""
    try:
        # Read input
        input_data = read_input(token, infile)
        if not input_data:
            typer.echo("Error: No input provided", err=True)
            raise typer.Exit(code=1)
        
        # Decode JWT without verification (as we only want to read the content)
        header = pyjwt.get_unverified_header(input_data)
        payload = pyjwt.decode(input_data, options={"verify_signature": False})
        
        # Format output
        result = f"Header:\n{header}\n\nPayload:\n{payload}"
        
        # Write output
        write_output(result, outfile)
        
    except Exception as e:
        typer.echo(f"Error decoding JWT: {str(e)}", err=True)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
