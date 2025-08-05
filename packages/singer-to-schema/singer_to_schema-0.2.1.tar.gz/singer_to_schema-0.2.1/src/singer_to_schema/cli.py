"""
Command-line interface for SingerToSchema.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from .singer_to_schema import SingerToSchema


def read_catalog_file(file_path: str) -> str:
    """
    Read catalog JSON from a file.
    
    Args:
        file_path: Path to the catalog JSON file
        
    Returns:
        JSON string content
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Catalog file not found: {file_path}")
    except UnicodeDecodeError:
        raise ValueError(f"Unable to read file as UTF-8: {file_path}")


def write_output(data: str, output_file: Optional[str] = None) -> None:
    """
    Write output to file or stdout.
    
    Args:
        data: Data to write
        output_file: Output file path (None for stdout)
    """
    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(data)
            print(f"Output written to: {output_file}", file=sys.stderr)
        except Exception as e:
            print(f"Error writing to output file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(data)


def main() -> None:
    """
    Main CLI entry point.
    """
    parser = argparse.ArgumentParser(
        description="Convert Singer catalog JSON to BigQuery table schema format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert catalog.json to BigQuery schema and print to stdout
  singer-to-schema catalog.json

  # Convert and save to output file
  singer-to-schema catalog.json -o bigquery_schema.json

  # Read from stdin and output to file
  cat catalog.json | singer-to-schema - -o schema.json

  # Pretty print the output
  singer-to-schema catalog.json --pretty
        """
    )
    
    parser.add_argument(
        'input',
        help='Input catalog JSON file (use "-" for stdin)'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output file (default: stdout)'
    )
    
    parser.add_argument(
        '--pretty',
        action='store_true',
        help='Pretty print the output JSON'
    )
    
    parser.add_argument(
        '--no-json-fields',
        action='store_true',
        help='Convert object and array fields to STRING instead of JSON'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 0.1.0'
    )
    
    args = parser.parse_args()
    
    try:
        # Read input
        if args.input == '-':
            # Read from stdin
            catalog_json = sys.stdin.read()
        else:
            # Read from file
            catalog_json = read_catalog_file(args.input)
        
        # Convert catalog
        use_json_fields = not args.no_json_fields
        converter = SingerToSchema(catalog_json, use_json_fields=use_json_fields)
        
        # Generate output
        if args.pretty:
            result = converter.to_bigquery_json()
        else:
            result = json.dumps(converter.to_bigquery())
        
        # Write output
        write_output(result, args.output)
        
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in catalog file: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main() 