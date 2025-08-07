# **Loki: Offline Developer CLI**

## About the Project (The "Why Loki?" Story)

> "Why Loki?
>
> Is it because this tool is a mischievous shapeshifter, masterfully transforming your data from one form to another—turning chaotic JSON into structured CSV, or decoding cryptic tokens into readable text?
>
> Or is it just a simple shorthand for a **Lo**cal **Ki**t of developer tools?
>
> The answer is yes."

## Features

* **JWT Decoding**: Decode JWT tokens to display their header and payload
* **SAML Decoding**: Decode Base64-encoded SAML Responses into readable XML
* **JSON Formatting**: Pretty-print JSON strings or files with customizable indentation
* **XML Formatting**: Pretty-print XML strings or files with standardized indentation
* **YAML Formatting**: Pretty-print YAML strings or files in canonical format
* **CSV/JSON Conversion**: Convert between CSV and JSON formats
* **Offline Operation**: All operations performed locally without internet connection
* **Intuitive CLI**: Nested subcommand structure with comprehensive help flags

## Installation

To install from source:

```bash
pip install .
```

For development installation:

```bash
pip install -e .
```

## Usage

### JWT Decoding

```bash
# Decode a JWT token
loki jwt decode <TOKEN>

# Or from stdin
cat token.txt | loki jwt decode
```

### SAML Decoding

```bash
# Decode a Base64-encoded SAML response
loki saml decode --infile saml.b64 --outfile decoded.xml
```

### JSON Formatting

```bash
# Format JSON with default indentation (2 spaces)
loki json format <JSON_DATA>

# Format JSON with custom indentation
cat data.json | loki json format --indent 4
```

### XML Formatting

```bash
# Format XML
loki xml format --infile messy.xml
```

### YAML Formatting

```bash
# Format YAML
cat config.yml | loki yaml format
```

### CSV to JSON Conversion

```bash
# Convert CSV to JSON
loki csv to-json --infile data.csv --outfile data.json
```

### JSON to CSV Conversion

```bash
# Convert JSON to CSV
cat data.json | loki csv to-csv --outfile data.csv
```
