import json
from typing import Dict, List, Any, Union


class SingerToSchema:
    """
    A class to convert Singer catalog JSON to BigQuery table schema format.
    """
    
    def __init__(self, catalog_json: str):
        """
        Initialize with a Singer catalog JSON string.
        
        Args:
            catalog_json: A JSON string containing Singer catalog data
        """
        self.catalog = json.loads(catalog_json)
        self._validate_catalog()
    
    def _validate_catalog(self) -> None:
        """
        Validate that the catalog has the expected structure.
        """
        if not isinstance(self.catalog, dict):
            raise ValueError("Catalog must be a JSON object")
        
        if "streams" not in self.catalog:
            raise ValueError("Catalog must contain 'streams' key")
        
        if not isinstance(self.catalog["streams"], list):
            raise ValueError("'streams' must be an array")
    
    def _convert_singer_type_to_bigquery(self, singer_type: Union[str, List[str]]) -> str:
        """
        Convert Singer type to BigQuery type.
        
        Args:
            singer_type: Singer type (string or array of strings)
            
        Returns:
            BigQuery type string
        """
        # Handle array of types (e.g., ["null", "string"])
        if isinstance(singer_type, list):
            # Filter out "null" and get the first non-null type
            non_null_types = [t for t in singer_type if t != "null"]
            if not non_null_types:
                return "STRING"  # Default if only null
            singer_type = non_null_types[0]
        
        # Map Singer types to BigQuery types
        type_mapping = {
            "string": "STRING",
            "integer": "INT64",
            "number": "FLOAT64",
            "boolean": "BOOL",
            "object": "JSON",
            "array": "JSON",
            "null": "STRING"  # Default for null-only fields
        }
        
        return type_mapping.get(singer_type, "STRING")
    
    def _process_schema_properties(self, properties: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Process schema properties and convert to BigQuery fields.
        
        Args:
            properties: Singer schema properties
            
        Returns:
            List of BigQuery field definitions
        """
        fields = []
        
        for field_name, field_schema in properties.items():
            field_type = field_schema.get("type")
            if not field_type:
                continue
            
            bigquery_type = self._convert_singer_type_to_bigquery(field_type)
            
            # Handle date-time format
            if isinstance(field_type, list) and "string" in field_type:
                format_type = field_schema.get("format")
                if format_type == "date-time":
                    bigquery_type = "TIMESTAMP"
                elif format_type == "date":
                    bigquery_type = "DATE"
                elif format_type == "time":
                    bigquery_type = "TIME"
            
            field_def = {
                "name": field_name,
                "type": bigquery_type,
                "mode": "NULLABLE"  # Default mode
            }
            
            fields.append(field_def)
        
        return fields
    
    def to_bigquery(self) -> Dict[str, Any]:
        """
        Convert Singer catalog to BigQuery table schema format.
        
        Returns:
            Dictionary containing BigQuery schema for each stream
        """
        result = {}
        
        for stream in self.catalog["streams"]:
            stream_id = stream.get("tap_stream_id") or stream.get("stream")
            if not stream_id:
                continue
            
            schema = stream.get("schema", {})
            properties = schema.get("properties", {})
            
            # Convert properties to BigQuery fields
            fields = self._process_schema_properties(properties)
            
            # Create BigQuery schema
            bigquery_schema = {
                "fields": fields
            }
            
            result[stream_id] = bigquery_schema
        
        return result
    
    def to_bigquery_json(self) -> str:
        """
        Convert Singer catalog to BigQuery table schema format as JSON string.
        
        Returns:
            JSON string containing BigQuery schema
        """
        return json.dumps(self.to_bigquery(), indent=2) 