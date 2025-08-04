# Singer to Schema

A Python library to convert Singer catalog JSON to BigQuery table schema format.

## Installation

```bash
pip install singer-to-schema
```

Or run directly with `uvx`.

```bash
uvx singer-to-schema --help
```

## Usage

The `SingerToSchema` class takes a Singer catalog JSON string and converts it to BigQuery table schema format.

### Command Line Interface

The package provides a command-line interface for easy conversion:

```bash
# Convert catalog.json to BigQuery schema and print to stdout
singer-to-schema catalog.json

# Convert and save to output file
singer-to-schema catalog.json -o bigquery_schema.json

# Read from stdin and output to file
cat catalog.json | singer-to-schema - -o schema.json

# Pretty print the output
singer-to-schema catalog.json --pretty

# Show help
singer-to-schema --help
```

### Library Usage

```python
from singer_to_schema import SingerToSchema

# Example Singer catalog JSON
catalog_json = '''{
  "streams": [
    {
      "tap_stream_id": "users",
      "stream": "users",
      "schema": {
        "type": ["null", "object"],
        "additionalProperties": false,
        "properties": {
          "id": {
            "type": ["null", "string"]
          },
          "name": {
            "type": ["null", "string"]
          },
          "date_modified": {
            "type": ["null", "string"],
            "format": "date-time"
          }
        }
      }
    }
  ]
}'''

# Create converter instance
converter = SingerToSchema(catalog_json)

# Convert to BigQuery schema format
bigquery_schema = converter.to_bigquery()
print(bigquery_schema)

# Or get as JSON string
json_schema = converter.to_bigquery_json()
print(json_schema)
```

### Output

The `to_bigquery()` method returns a dictionary with the following structure:

```json
{
  "users": {
    "fields": [
      {
        "name": "id",
        "type": "STRING",
        "mode": "NULLABLE"
      },
      {
        "name": "name",
        "type": "STRING",
        "mode": "NULLABLE"
      },
      {
        "name": "date_modified",
        "type": "TIMESTAMP",
        "mode": "NULLABLE"
      }
    ]
  }
}
```

## Type Mapping

The library maps Singer types to BigQuery types as follows:

| Singer Type | BigQuery Type |
|-------------|---------------|
| `string` | `STRING` |
| `integer` | `INT64` |
| `number` | `FLOAT64` |
| `boolean` | `BOOL` |
| `object` | `JSON` |
| `array` | `JSON` |

### Date/Time Formats

When a string field has a `format` property, it's mapped to appropriate BigQuery types:

| Format | BigQuery Type |
|--------|---------------|
| `date-time` | `TIMESTAMP` |
| `date` | `DATE` |
| `time` | `TIME` |

## API Reference

### SingerToSchema

#### `__init__(catalog_json: str)`

Initialize the converter with a Singer catalog JSON string.

**Parameters:**
- `catalog_json`: A JSON string containing Singer catalog data

**Raises:**
- `ValueError`: If the catalog structure is invalid
- `json.JSONDecodeError`: If the JSON is malformed

#### `to_bigquery() -> Dict[str, Any]`

Convert the Singer catalog to BigQuery table schema format.

**Returns:**
- Dictionary containing BigQuery schema for each stream

#### `to_bigquery_json() -> str`

Convert the Singer catalog to BigQuery table schema format as a JSON string.

**Returns:**
- JSON string containing BigQuery schema

## Development

### Running Tests

```bash
uv run pytest
```

## License

This project is licensed under the MIT License.
