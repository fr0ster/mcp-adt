import xmltodict
from requests.exceptions import HTTPError, RequestException
from .utils import AdtError, make_session, SAP_URL, SAP_CLIENT

# JSON schema for Gemini function‐calling
get_package_structure_definition = {
    "name": "get_package_structure",
    "description": "Retrieve the list of objects in an ABAP package via the ADT repository nodestructure service.",
    "parameters": {
        "type": "object",
        "properties": {
            "package_name": {
                "type": "string",
                "description": "Name of the ABAP package (e.g. 'ZMY_PACKAGE')."
            }
        },
        "required": ["package_name"]
    }
}

def get_package_structure(
    package_name: str
) -> list[dict]:
    """
    Fetches the structure (objects) under an ABAP package via ADT.

    - First does a GET with X-CSRF-Token: Fetch to retrieve the token.
    - Then POSTs to /sap/bc/adt/repository/nodestructure?parent_type=DEVC/K&parent_name=...
      including the X-CSRF-Token header.
    - Parses the returned XML into a list of dicts with keys:
      OBJECT_TYPE, OBJECT_NAME, OBJECT_DESCRIPTION, OBJECT_URI.
    - Raises AdtError on HTTP errors; ConnectionError on network failures.
    """
    print(f"Fetching package structure for {package_name}")
    if not package_name:
        raise ValueError("package_name is required")

    session = make_session()
    endpoint = f"{SAP_URL.rstrip('/')}/sap/bc/adt/repository/nodestructure"
    params = {
        "sap-client":          SAP_CLIENT,
        "parent_type":         "DEVC/K",
        "parent_name":         package_name,
        "withShortDescriptions": "true"
    }

    # 1) Fetch CSRF token via a GET
    try:
        fetch_resp = session.get(
            endpoint,
            params=params,
            headers={"X-CSRF-Token": "Fetch", "Accept": "*/*"}
        )
        # even if fetch_resp.status_code is 405 or 404, it may still return the token header
        token = fetch_resp.headers.get("X-CSRF-Token")
    except RequestException as e:
        raise ConnectionError(f"Failed to fetch CSRF token: {e}") from e

    # 2) Now POST with that token (if present)
    post_headers = {}
    if token:
        post_headers["X-CSRF-Token"] = token

    try:
        resp = session.post(
            endpoint,
            params=params,
            headers=post_headers
        )
        resp.raise_for_status()
    except HTTPError as e:
        if resp.status_code == 404:
            raise AdtError(404, f"Package '{package_name}' not found") from e
        if resp.status_code == 403:
            raise AdtError(403, "Access forbidden: CSRF token missing or invalid") from e
        raise

    # 3) Parse the XML
    doc = xmltodict.parse(resp.text)
    nodes = (
        doc.get("asx:abap", {})
           .get("asx:values", {})
           .get("DATA", {})
           .get("TREE_CONTENT", {})
           .get("SEU_ADT_REPOSITORY_OBJ_NODE", [])
    )
    items = nodes if isinstance(nodes, list) else [nodes]

    # 4) Extract and filter
    result = []
    for n in items:
        name = n.get("OBJECT_NAME")
        uri  = n.get("OBJECT_URI")
        if not name or not uri:
            continue
        result.append({
            "OBJECT_TYPE":        n.get("OBJECT_TYPE"),
            "OBJECT_NAME":        name,
            "OBJECT_DESCRIPTION": n.get("DESCRIPTION"),
            "OBJECT_URI":         uri
        })

    return result
