Excel MCP Server (python-calamine)
A high-performance, read-only MCP server for efficient access to Excel files (.xlsx, .xls, .ods).
Built on fastmcp and python-calamine, it’s designed as a faster, safer alternative to excel-mcp-server (no openpyxl), giving huge speedups on large files.

Note:
The python-calamine library is read-only. This server can extract data from files, but cannot modify or save them.

🚀 Key Features
High Performance:
Powered by the Rust-based python-calamine library for lightning-fast reads, even on huge Excel files.

Asynchronous:
Based on fastmcp for scalable, async request handling.

Read-Only Safety:
Guarantees your source files stay untouched.

In-Memory Caching:
Workbooks are cached to speed up repeated reads.

Easy Deployment:
Containerized with Docker and Docker Compose.
The code now automatically supports both old and new versions of
``fastmcp``. If you encounter import errors related to ``Mcp`` or ``Mq``,
make sure the library is up to date.

🗂 Project Structure
bash
Копировать
Редактировать
/opt/excel-mcp/
├── calamine_mcp/        # Application source code
│   ├── __init__.py      # Python package marker
│   ├── cli.py           # CLI (server startup)
│   ├── server.py        # Core MCP server/handlers
│   └── workbook.py      # Excel abstraction via calamine
├── docker-compose.yml   # Docker Compose orchestration
├── Dockerfile           # Docker build instructions
├── pyproject.toml       # Project definition/deps
└── requirements.txt     # Dependency list (Docker caching)
⚙️ Requirements
Docker

Docker Compose

🐳 Deployment
1. Create Project Directories
bash
Копировать
Редактировать
mkdir -p /opt/excel-mcp/calamine_mcp
cd /opt/excel-mcp
2. Add Project Files
Copy all files from this repository into /opt/excel-mcp.
The Dockerfile must be next to docker-compose.yml for correct builds.

3. Prepare Excel Files Directory
Make sure the directory to be mounted as a volume exists:

bash
Копировать
Редактировать
mkdir -p /home/ubuntu/excel-files
# Place your .xlsx, .xls, or .ods files here
cp /path/to/your/file.xlsx /home/ubuntu/excel-files/
4. Run the Service
From /opt/excel-mcp:

bash
Копировать
Редактировать
docker-compose up --build -d
This builds the Docker image and starts the service in detached mode.

⚙️ Configuration
Server settings are controlled via environment variables in docker-compose.yml:

EXCEL_FILES_PATH:
Path inside the container where Excel files are available. Should match the mount target.

UID & GID:
User/group IDs used inside the container. Set to your host’s UID/GID (id -u, id -g) for correct file permissions.

🛠 Server API (MCP Handlers)
get_sheet_names
Returns a list of all sheet names in a file.

Request:

json
Копировать
Редактировать
{ "method": "get_sheet_names", "params": {"filename": "my_file.xlsx"} }
Response:

json
Копировать
Редактировать
["Sheet1", "Sheet2", "Data"]
get_cell
Retrieves the value of a single cell.

Request:

json
Копировать
Редактировать
{
  "method": "get_cell",
  "params": {
    "filename": "my_file.xlsx",
    "sheet_name": "Sheet1",
    "row": 1,
    "col": 1
  }
}
Response:
Value of cell A1

get_all_rows
Returns all rows of a sheet as a 2D list.

Request:

json
Копировать
Редактировать
{
  "method": "get_all_rows",
  "params": {
    "filename": "my_file.xlsx",
    "sheet_name": "Sheet1"
  }
}
Response:

json
Копировать
Редактировать
[
  ["A1", "B1"],
  ["A2", "B2"]
]
get_file_metadata
Returns metadata about the file.

Request:

json
Копировать
Редактировать
{ "method": "get_file_metadata", "params": {"filename": "my_file.xlsx"} }
Response:

json
Копировать
Редактировать
{
  "size": 12345,
  "modified_at": 1678886400.0,
  "is_readonly": true
}
Error Responses
If an error occurs (e.g., file not found), the server returns an error field:

json
Копировать
Редактировать
{ "error": "File not found at path: /app/backend/data/uploads/non_existent_file.xlsx" }
❤️ Enjoy super-fast, safe, and simple Excel data access with python-calamine and fastmcp!
