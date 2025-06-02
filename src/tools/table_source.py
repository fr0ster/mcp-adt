import xmltodict
from .utils import AdtError, make_session, SAP_URL, SAP_CLIENT, encode_sap_object_name

# JSON schema for Gemini function‐calling
get_table_source_definition = {
    "name": "get_table_source",
    "description": "Retrieve source code lines for an ABAP DDIC table via ADT, with XML and text/plain fallback.",
    "parameters": {
        "type": "object",
        "properties": {
            "table_name": {
                "type": "string",
                "description": "Name of the ABAP DDIC table (e.g. 'ZMY_TABLE')."
            }
        },
        "required": ["table_name"]
    }
}

def get_table_source(
    table_name: str
) -> list[str]:
    """
    Fetches the source lines of an ABAP DDIC table via the ADT API.

    - Tries XML (ADT payload) first.
    - On 406 Not Acceptable, retries with plain text.
    - Raises AdtError on 404/not found; ConnectionError on network failures.
    """
    print(f"Fetching table source for {table_name}")
    if not table_name:
        raise ValueError("table_name is required")

    session = make_session()
    base     = SAP_URL.rstrip('/')
    encoded_table_name = encode_sap_object_name(table_name)
    endpoint = f"{base}/sap/bc/adt/ddic/tables/{encoded_table_name}/source/main"
    params   = {"sap-client": SAP_CLIENT}
    hdr_xml  = {"Accept": "application/vnd.sap.adt.abapsource+xml"}
    hdr_txt  = {"Accept": "text/plain"}

    # 1) Try XML payload
    resp = session.get(endpoint, params=params, headers=hdr_xml)
    if resp.status_code == 406:
        # 2) Fallback to plain text
        resp2 = session.get(endpoint, params=params, headers=hdr_txt)
        resp2.raise_for_status()
        return resp2.text.splitlines()

    try:
        resp.raise_for_status()
    except Exception as e:
        if resp.status_code == 404:
            raise AdtError(404, f"Table '{table_name}' not found") from e
        raise

    # 3) Parse ADT XML into a list of lines
    doc   = xmltodict.parse(resp.text)
    lines = doc['adtcore:abapsource']['objectSource']['line']
    if isinstance(lines, str):
        return [lines]
    return [ln.get('#text', '') for ln in lines]
