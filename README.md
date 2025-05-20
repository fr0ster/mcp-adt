# ADT MCP Server

This repository provides a Model Context Protocol (MCP) server for ABAP Development Tools (ADT), exposing various ABAP repository-read tools (program, class, function, include, interface, structure, table, where-used, etc.) over a standardized MCP interface.

---

## Prerequisites

* **Python 3.9+**
* **pip** (the Python package installer)
* A running SAP ABAP system with ADT services enabled
* A `.env` file in the project root with your SAP connection settings (see below)

## Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/<your-org>/<your-repo>.git
   cd <your-repo>
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Linux/macOS
   .\.venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**

   Create a **requirements.txt** file in the project root with the following contents:

   ```text
   mcp-server
   python-dotenv
   requests
   ```

   Then install:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Copy the example `.env.example` to `.env` and fill in your SAP credentials:

   ```ini
   SAP_URL=https://my.sap.system:443
   SAP_CLIENT=100
   SAP_USERNAME=YOUR_USER
   SAP_PASSWORD=YOUR_PASS
   ```

## Usage

Run the MCP server over stdio transport:

```bash
python mcp_server.py
```

By default, it listens for MCP JSON-RPC calls on STDIO. Each tool is exposed as a method you can call. For example, to retrieve an ABAP class source:

```json
{
  "jsonrpc": "2.0",
  "method": "GetClass",
  "params": {
    "class_name": "ZCL_MY_CLASS"
  },
  "id": 1
}
```

### Available Tools

* `GetProgram` – Retrieve ABAP program source
* `GetClass` – Retrieve ABAP class source
* `GetFunctionGroup` – Retrieve function group source
* `GetFunction` – Retrieve function module source
* `GetInclude` – Retrieve include source
* `GetInterface` – Retrieve interface source
* `GetStructure` – Retrieve structure definition
* `GetTable` – Retrieve table definition
* `GetTableContents` – Fetch table data (max rows default 100)
* `GetPackage` – Retrieve package metadata
* `GetTypeInfo` – Retrieve type information
* `GetTransaction` – Retrieve transaction properties
* `SearchObject` – Quick search for repository objects
* `GetUsageReferences` – Retrieve where‑used references for any object

## License

[MIT](LICENSE)
