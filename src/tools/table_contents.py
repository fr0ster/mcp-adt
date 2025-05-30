# tools/table_contents.py

import xmltodict
from typing import Dict, List, Any, Optional
from requests.exceptions import HTTPError, RequestException
from .utils import AdtError, make_session, SAP_URL, SAP_CLIENT

# JSON schema for MCP function-calling
get_table_contents_definition = {
    "name": "get_table_contents",
    "description": "Retrieve table contents via ADT Data Preview API with proper SQL generation.",
    "parameters": {
        "type": "object",
        "properties": {
            "table_name": {
                "type": "string",
                "description": "Name of the ABAP table (e.g. 'T000')."
            },
            "max_rows": {
                "type": "integer", 
                "description": "Maximum number of rows to retrieve (default: 100).",
                "default": 100
            }
        },
        "required": ["table_name"]
    }
}

def _get_table_fields(table_name: str, session) -> List[str]:
    """
    Get table field list from CDS source or table structure.
    Returns list of field names for SQL generation.
    """
    print(f"Getting field list for table {table_name}")
    
    # Try to get CDS source first
    try:
        cds_url = f"{SAP_URL.rstrip('/')}/sap/bc/adt/ddic/ddl/sources/{table_name}/source/main"
        resp = session.get(
            cds_url,
            params={"sap-client": SAP_CLIENT},
            headers={"Accept": "text/plain"}
        )
        
        if resp.status_code == 200:
            # Parse CDS field definitions
            fields = []
            lines = resp.text.splitlines()
            
            for line in lines:
                line = line.strip()
                # Look for field definitions - pattern: fieldname : type;
                if ':' in line and ';' in line and not line.startswith('//'):
                    field_part = line.split(':')[0].strip()
                    if field_part and not field_part.startswith('@'):
                        fields.append(field_part.upper())
            
            if fields:
                print(f"Found {len(fields)} fields from CDS source")
                return fields
                
    except Exception as e:
        print(f"Failed to get CDS source: {e}")
    
    # Fallback: try to get table structure
    try:
        table_url = f"{SAP_URL.rstrip('/')}/sap/bc/adt/ddic/tables/{table_name}/source/main"
        resp = session.get(
            table_url,
            params={"sap-client": SAP_CLIENT},
            headers={"Accept": "application/vnd.sap.adt.abapsource+xml"}
        )
        
        if resp.status_code == 200:
            # Parse table structure XML
            doc = xmltodict.parse(resp.text)
            lines = doc.get('adtcore:abapsource', {}).get('objectSource', {}).get('line', [])
            
            fields = []
            in_structure = False
            
            if isinstance(lines, list):
                for line_obj in lines:
                    line = line_obj.get('#text', '') if isinstance(line_obj, dict) else str(line_obj)
                    line = line.strip()
                    
                    if 'begin of' in line.lower() or 'data:' in line.lower():
                        in_structure = True
                        continue
                    elif 'end of' in line.lower():
                        break
                    elif in_structure and line and not line.startswith('*'):
                        # Extract field name from ABAP declaration
                        parts = line.split()
                        if len(parts) > 0:
                            field_name = parts[0].rstrip(',').upper()
                            if field_name and field_name not in ['DATA', 'TYPES']:
                                fields.append(field_name)
            
            if fields:
                print(f"Found {len(fields)} fields from table structure")
                return fields
                
    except Exception as e:
        print(f"Failed to get table structure: {e}")
    
    # Ultimate fallback: return common fields
    print("Using fallback field list")
    return ["MANDT", "CLIENT"]

def _generate_sql_query(table_name: str, fields: List[str]) -> str:
    """
    Generate SQL SELECT statement with table-prefixed field names.
    Format: SELECT T000~MANDT, T000~FIELD2, ... FROM T000
    """
    if not fields:
        return f"SELECT * FROM {table_name}"
    
    # Create table-prefixed field list
    prefixed_fields = [f"{table_name}~{field}" for field in fields]
    field_list = ", ".join(prefixed_fields)
    
    sql = f"SELECT {field_list} FROM {table_name}"
    print(f"Generated SQL: {sql}")
    return sql

def _parse_table_data_xml(xml_data: str, table_name: str) -> Dict[str, Any]:
    """
    Parse SAP ADT XML response and convert to JSON format with rows.
    """
    try:
        # Extract basic information
        total_rows_match = xml_data.find('<dataPreview:totalRows>')
        total_rows = 0
        if total_rows_match != -1:
            end_match = xml_data.find('</dataPreview:totalRows>', total_rows_match)
            if end_match != -1:
                total_rows_str = xml_data[total_rows_match + 23:end_match]
                total_rows = int(total_rows_str) if total_rows_str.isdigit() else 0

        query_time_match = xml_data.find('<dataPreview:queryExecutionTime>')
        execution_time = 0.0
        if query_time_match != -1:
            end_match = xml_data.find('</dataPreview:queryExecutionTime>', query_time_match)
            if end_match != -1:
                time_str = xml_data[query_time_match + 32:end_match]
                try:
                    execution_time = float(time_str)
                except ValueError:
                    execution_time = 0.0

        # Extract column metadata
        columns = []
        import re
        column_matches = re.findall(r'<dataPreview:metadata[^>]*>', xml_data)
        
        for match in column_matches:
            name_match = re.search(r'dataPreview:name="([^"]+)"', match)
            type_match = re.search(r'dataPreview:type="([^"]+)"', match)
            desc_match = re.search(r'dataPreview:description="([^"]+)"', match)
            length_match = re.search(r'dataPreview:length="(\d+)"', match)
            
            if name_match:
                columns.append({
                    "name": name_match.group(1),
                    "type": type_match.group(1) if type_match else "UNKNOWN",
                    "description": desc_match.group(1) if desc_match else "",
                    "length": int(length_match.group(1)) if length_match else None
                })

        # Extract row data
        rows = []
        column_sections = re.findall(r'<dataPreview:columns>.*?</dataPreview:columns>', xml_data, re.DOTALL)
        
        if column_sections:
            # Extract data for each column
            column_data = {}
            
            for index, section in enumerate(column_sections):
                if index < len(columns):
                    column_name = columns[index]["name"]
                    data_matches = re.findall(r'<dataPreview:data[^>]*>(.*?)</dataPreview:data>', section)
                    
                    if data_matches:
                        # Clean HTML tags and get content
                        column_data[column_name] = [
                            re.sub(r'<[^>]+>', '', match) if match else None 
                            for match in data_matches
                        ]
                    else:
                        column_data[column_name] = []

            # Convert column-based data to row-based data
            if column_data:
                max_row_count = max(len(arr) for arr in column_data.values()) if column_data else 0
                
                for row_index in range(max_row_count):
                    row = {}
                    for column in columns:
                        column_values = column_data.get(column["name"], [])
                        row[column["name"]] = column_values[row_index] if row_index < len(column_values) else None
                    rows.append(row)

        return {
            "table_name": table_name,
            "total_rows": total_rows,
            "execution_time": execution_time,
            "columns": columns,
            "rows": rows,
            "row_count": len(rows)
        }

    except Exception as parse_error:
        print(f"Failed to parse table data XML: {parse_error}")
        return {
            "table_name": table_name,
            "total_rows": 0,
            "execution_time": 0.0,
            "columns": [],
            "rows": [],
            "row_count": 0,
            "parse_error": str(parse_error)
        }

def get_table_contents(table_name: str, max_rows: int = 100) -> Dict[str, Any]:
    """
    Retrieve table contents via ADT Data Preview API.
    
    - Gets table field structure first
    - Generates proper SQL SELECT with table-prefixed fields
    - POSTs SQL query to data preview endpoint
    - Parses XML response into structured JSON
    """
    print(f"Getting table contents for {table_name}, max_rows: {max_rows}")
    
    if not table_name:
        raise ValueError("table_name is required")

    session = make_session()
    
    try:
        # Step 1: Get table fields
        fields = _get_table_fields(table_name, session)
        
        # Step 2: Generate SQL query
        sql_query = _generate_sql_query(table_name, fields)
        
        # Step 3: Execute query via data preview API
        endpoint = f"{SAP_URL.rstrip('/')}/sap/bc/adt/datapreview/freestyle"
        params = {
            "sap-client": SAP_CLIENT,
            "rowNumber": str(max_rows)
        }
        headers = {
            "Content-Type": "text/plain; charset=utf-8",
            "Accept": "application/vnd.sap.adt.datapreview.v1+xml"
        }
        
        print(f"Making POST request to: {endpoint}")
        print(f"SQL Query: {sql_query}")
        
        resp = session.post(
            endpoint,
            params=params,
            headers=headers,
            data=sql_query
        )
        
        resp.raise_for_status()
        
        # Step 4: Parse response
        if resp.status_code == 200 and resp.text:
            parsed_data = _parse_table_data_xml(resp.text, table_name)
            print(f"Successfully retrieved {parsed_data.get('row_count', 0)} rows")
            return parsed_data
        else:
            raise AdtError(resp.status_code, f"Failed to retrieve table contents. Status: {resp.status_code}")
            
    except HTTPError as e:
        if e.response.status_code == 404:
            raise AdtError(404, f"Table '{table_name}' not found") from e
        raise AdtError(e.response.status_code, e.response.text) from e
    except RequestException as e:
        raise ConnectionError(f"Network error retrieving table contents: {e}") from e
