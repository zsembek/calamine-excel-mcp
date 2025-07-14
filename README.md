Excel MCP Server (python-calamine)
A high-performance MCP server built on fastmcp and python-calamine, designed for efficient, read-only access to Excel files (.xlsx, .xls, .ods).
This project was created as an alternative to excel-mcp-server, but without using openpyxl, resulting in significantly higher speeds on large files.

Note:
The python-calamine library is read-only. This server can only extract data from files and does not support modifying or saving them.

🚀 Key Features
High Performance:
Uses python-calamine, a Rust-powered library for Python, ensuring extremely fast reading of even very large Excel files.

Asynchronous:
Built on fastmcp, allowing the server to handle many requests asynchronously and efficiently.

Read-Only Safety:
Ideal for scenarios where you only need to extract data, ensuring the original files remain unmodified.

In-Memory Caching:
Opened workbooks are cached in memory to reduce disk reads and accelerate repeated access.

Easy Deployment:
Fully containerized and ready to run with Docker and Docker Compose.

🗂 Project Structure
bash
Копировать
Редактировать
/opt/excel-mcp/
├── calamine_mcp/           # Application source code
│   ├── __init__.py         # Python package marker
│   ├── cli.py              # Command-line interface (server startup)
│   ├── server.py           # Core MCP server and request handlers
│   └── workbook.py         # Abstraction for Excel access via calamine
├── docker-compose.yml      # Docker Compose orchestration
├── Dockerfile              # Docker image build instructions
├── pyproject.toml          # Project definition and dependencies
└── requirements.txt        # Dependency list for Docker caching
⚙️ Requirements
Docker

Docker Compose

🐳 Deployment
1. Create Project Directories
sh
Копировать
Редактировать
mkdir -p /opt/excel-mcp/calamine_mcp
cd /opt/excel-mcp
2. Add Project Files
Copy the project files (as shown in the structure above) into their respective directories.

3. Prepare Excel Files Directory
Ensure the directory to be mounted as a volume exists. For example:

sh
Копировать
Редактировать
mkdir -p /home/ubuntu/excel-files
# Place your .xlsx, .xls, or .ods files here
cp /path/to/your/file.xlsx /home/ubuntu/excel-files/
4. Run the Service
From /opt/excel-mcp:

sh
Копировать
Редактировать
docker-compose up --build -d
This command builds the Docker image and starts the service in detached mode.

⚙️ Configuration
Server configuration is handled via environment variables in docker-compose.yml:

EXCEL_FILES_PATH:
Internal container path for the directory containing Excel files. Must match the target of your mounted volume.

UID & GID:
User and group IDs for running the process inside the container. Set these to match your host user (id -u, id -g) to ensure correct permissions.

🛠 Server API (MCP Handlers)
The server provides the following handlers:

get_sheet_names
Returns a list of all sheet names in a file.

Request:

json
Копировать
Редактировать
{
  "method": "get_sheet_names",
  "params": {"filename": "my_file.xlsx"}
}
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
{
  "method": "get_file_metadata",
  "params": {"filename": "my_file.xlsx"}
}
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
If an error occurs (e.g., file not found), the server returns a response with an error field:

json
Копировать
Редактировать
{
  "error": "File not found at path: /app/backend/data/uploads/non_existent_file.xlsx"
}
Enjoy super-fast, safe, and simple Excel data access with python-calamine and fastmcp!
