#!/usr/bin/env python3

"""CSV command module for Loki CLI"""

import sys
import json as json_lib
import pandas as pd
import typer
from typing import Optional

app = typer.Typer(help="CSV/JSON conversion operations")


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
def to_json(
    infile: Optional[str] = typer.Option(None, "--infile", "-i", help="Input CSV file path (required if not using stdin)"),
    outfile: Optional[str] = typer.Option(None, "--outfile", "-o", help="Output JSON file path"),
):
    """Converts CSV data into a JSON array of objects"""
    try:
        # Read input
        if not infile and sys.stdin.isatty():
            typer.echo("Error: --infile is required when not piping data", err=True)
            raise typer.Exit(code=1)
        
        # Read CSV using pandas
        if infile:
            df = pd.read_csv(infile)
        else:
            # Read from stdin
            csv_data = sys.stdin.read()
            from io import StringIO
            df = pd.read_csv(StringIO(csv_data))
        
        # Convert to JSON
        json_data = df.to_json(orient='records', indent=2)
        
        # Write output
        write_output(json_data, outfile)
        
    except Exception as e:
        typer.echo(f"Error converting CSV to JSON: {str(e)}", err=True)
        raise typer.Exit(code=1)


@app.command()
def to_csv(
    infile: Optional[str] = typer.Option(None, "--infile", "-i", help="Input JSON file path (required if not using stdin)"),
    outfile: Optional[str] = typer.Option(None, "--outfile", "-o", help="Output CSV file path"),
):
    """Converts a JSON array of flat objects into CSV data"""
    try:
        # Read input
        if not infile and sys.stdin.isatty():
            typer.echo("Error: --infile is required when not piping data", err=True)
            raise typer.Exit(code=1)
        
        # Read JSON data
        if infile:
            with open(infile, 'r') as f:
                json_data = f.read()
        else:
            # Read from stdin
            json_data = sys.stdin.read()
        
        # Parse JSON
        parsed_json = json_lib.loads(json_data)
        
        # Validate JSON structure
        if not isinstance(parsed_json, list):
            typer.echo("Error: JSON must be an array of objects", err=True)
            raise typer.Exit(code=1)
        
        if not all(isinstance(item, dict) for item in parsed_json):
            typer.echo("Error: All items in JSON array must be objects", err=True)
            raise typer.Exit(code=1)
        
        # Convert to CSV using pandas
        df = pd.DataFrame(parsed_json)
        csv_data = df.to_csv(index=False)
        
        # Write output
        write_output(csv_data, outfile)
        
    except Exception as e:
        typer.echo(f"Error converting JSON to CSV: {str(e)}", err=True)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
