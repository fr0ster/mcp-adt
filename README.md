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

   ```text
   pip install mcp "mcp[cli]"
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
   SAP_USER=YOUR_USER
   SAP_PASS=YOUR_PASS
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
