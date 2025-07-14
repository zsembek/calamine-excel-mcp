This is a high-performance MCP server built on fastmcp and python-calamine, designed for reading data from Excel files (.xlsx, .xls, .ods). The project was created as an alternative to excel-mcp-server but without using openpyxl, which provides significantly higher read speeds for large files.

Important Note: The python-calamine library is read-only. This means the server can only extract data from files and does not support operations to modify or save them.

Key Features
High Performance: Uses python-calamine, a Rust-based library for Python, ensuring extremely fast reading of even very large Excel files.

Asynchronous: The server is built on fastmcp, allowing it to handle numerous requests asynchronously and efficiently.

Read-Only: Designed for tasks that only require data extraction, making it safe to use with original source files.

Caching: Open workbooks are cached in memory to minimize disk operations on repeated requests to the same file.

Easy Deployment: The project is fully containerized and ready for deployment using Docker and Docker Compose.

Project Structure
/opt/excel-mcp/
├── calamine_mcp/           # Application source code
│   ├── __init__.py         # Makes the directory a Python package
│   ├── cli.py              # Command-Line Interface (CLI) for starting the server
│   ├── server.py           # Core MCP server logic and request handlers
│   └── workbook.py         # Abstraction for working with Excel files via calamine
├── docker-compose.yml      # File for Docker container orchestration
├── Dockerfile              # Instructions for building the Docker image
├── pyproject.toml          # Project definition and dependencies (PEP 621)
└── requirements.txt        # List of dependencies for Docker layer caching

Requirements
Docker

Docker Compose

Deployment
Create Project Directories:

mkdir -p /opt/excel-mcp/calamine_mcp
cd /opt/excel-mcp

Create Files: Save all the previously provided files into their respective directories according to the project structure.

Prepare Excel Files Directory: Ensure the directory you are mounting as a volume (in docker-compose.yml, this is /home/ubuntu/excel-files) exists.

mkdir -p /home/ubuntu/excel-files
# Place your .xlsx or .xls files in this folder
cp /path/to/your/file.xlsx /home/ubuntu/excel-files/

Run the Service: From the /opt/excel-mcp directory, execute the command:

docker-compose up --build -d

This command will build the Docker image and then create and run the container in detached mode.

Configuration
The server is configured via environment variables in the docker-compose.yml file:

EXCEL_FILES_PATH: The internal path within the container to the directory containing Excel files. This must match the target path of the mounted volume.

UID and GID: The user and group IDs under which the process will run inside the container. This is necessary to ensure correct file permissions on the mounted volume. Set these to match your user on the host machine (id -u and id -g).

Server API (MCP Handlers)
The server provides the following handlers:

get_sheet_names
Returns a list of all sheet names in a file.

Request: {'method': 'get_sheet_names', 'params': {'filename': 'my_file.xlsx'}}

Response: ['Sheet1', 'Sheet2', 'Data']

get_cell
Retrieves the value of a single cell.

Request: {'method': 'get_cell', 'params': {'filename': 'my_file.xlsx', 'sheet_name': 'Sheet1', 'row': 1, 'col': 1}}

Response: Value of cell A1

get_all_rows
Returns all rows of a sheet as a 2D list.

Request: {'method': 'get_all_rows', 'params': {'filename': 'my_file.xlsx', 'sheet_name': 'Sheet1'}}

Response: [['A1', 'B1'], ['A2', 'B2']]

get_file_metadata
Returns metadata about the file.

Request: {'method': 'get_file_metadata', 'params': {'filename': 'my_file.xlsx'}}

Response: {'size': 12345, 'modified_at': 1678886400.0, 'is_readonly': True}

In case of an error (e.g., file not found), the server will return a response with an error field.

Error Response: {'error': 'File not found at path: /app/backend/data/uploads/non_existent_file.xlsx'}
