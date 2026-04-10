# Architecture

## System Overview

```mermaid
graph TB
    subgraph "User Interfaces"
        CLI["CLI (obs)<br/>cli_obsidian"]
        MCP["MCP Server<br/>mcp_obsidian"]
    end

    subgraph "Core Library"
        Client["Obsidian Client<br/>obsidian.py"]
        Tools["Tool Handlers<br/>tools.py"]
    end

    subgraph "External"
        Plugin["Obsidian Local REST API<br/>Plugin (port 27124)"]
        Vault["Obsidian Vault<br/>Files & Folders"]
    end

    CLI --> Client
    MCP --> Tools
    Tools --> Client
    Client -->|HTTP/2| Plugin
    Plugin --> Vault
```

## Component Details

### CLI Package (`cli_obsidian`)

```mermaid
graph LR
    subgraph "cli_obsidian"
        Main["__init__.py<br/>Entry point"]
        Commands["cli.py<br/>Click commands"]
        Output["output.py<br/>Formatting"]
    end

    Main --> Commands
    Commands --> Output
    Commands -->|imports| ObsClient["Obsidian Client"]
```

**Responsibilities:**
- Parse command-line arguments via Click
- Format output for human or JSON consumption
- Handle environment variables and configuration

**Key Files:**
- `cli.py` - 11 Click commands (list-files, get, search, etc.)
- `output.py` - Output formatting helpers (print_json, print_error, etc.)

### MCP Server Package (`mcp_obsidian`)

```mermaid
graph LR
    subgraph "mcp_obsidian"
        ServerMain["__init__.py<br/>Entry point"]
        Server["server.py<br/>MCP setup"]
        ToolHandlers["tools.py<br/>13 tool handlers"]
        Client["obsidian.py<br/>HTTP client"]
    end

    ServerMain --> Server
    Server --> ToolHandlers
    ToolHandlers --> Client
```

**Responsibilities:**
- Implement Model Context Protocol (MCP) interface
- Expose 13 tools for AI assistants
- Handle tool invocation and response formatting

**Key Files:**
- `server.py` - MCP server initialization
- `tools.py` - ToolHandler classes for each operation
- `obsidian.py` - HTTP/2 client for REST API

### Obsidian Client (`obsidian.py`)

```mermaid
classDiagram
    class Obsidian {
        +api_key: str
        +protocol: str
        +host: str
        +port: int
        +verify_ssl: bool
        +client: httpx.Client
        
        +list_files_in_vault() list
        +list_files_in_dir(dirpath) list
        +get_file_contents(filepath) str
        +get_batch_file_contents(filepaths) str
        +search(query, context_length) list
        +search_json(query) list
        +put_content(filepath, content) None
        +append_content(filepath, content) None
        +patch_content(...) None
        +delete_file(filepath) None
        +get_periodic_note(period, type) str
        +get_recent_periodic_notes(period, limit, include_content) list
        +get_recent_changes(limit, days) list
        +close() None
    }
```

**Features:**
- Lazy-initialized httpx.Client with HTTP/2 support
- Automatic error handling and response parsing
- Environment-based configuration

## Data Flow

### Read Operation (get file)

```mermaid
sequenceDiagram
    participant User
    participant CLI/MCP
    participant Client
    participant Plugin
    participant Vault

    User->>CLI/MCP: obs get "note.md"
    CLI/MCP->>Client: get_file_contents("note.md")
    Client->>Plugin: GET /vault/note.md
    Plugin->>Vault: Read file
    Vault-->>Plugin: File content
    Plugin-->>Client: HTTP 200 + content
    Client-->>CLI/MCP: content string
    CLI/MCP-->>User: Display content
```

### Write Operation (put content)

```mermaid
sequenceDiagram
    participant User
    participant CLI/MCP
    participant Client
    participant Plugin
    participant Vault

    User->>CLI/MCP: obs put "note.md" "content"
    CLI/MCP->>Client: put_content("note.md", "content")
    Client->>Plugin: PUT /vault/note.md
    Plugin->>Vault: Write file
    Vault-->>Plugin: Success
    Plugin-->>Client: HTTP 200
    Client-->>CLI/MCP: None
    CLI/MCP-->>User: "Created/updated note.md"
```

### Search Operation

```mermaid
sequenceDiagram
    participant User
    participant CLI/MCP
    participant Client
    participant Plugin

    User->>CLI/MCP: obs search "query"
    CLI/MCP->>Client: search("query", 100)
    Client->>Plugin: POST /search/simple/?query=...
    Plugin-->>Client: HTTP 200 + results JSON
    Client-->>CLI/MCP: results list
    CLI/MCP-->>User: Formatted results
```

## API Endpoints

The client communicates with these Obsidian Local REST API endpoints:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/vault/` | List vault root |
| GET | `/vault/{path}/` | List directory |
| GET | `/vault/{path}` | Get file content |
| PUT | `/vault/{path}` | Create/overwrite file |
| POST | `/vault/{path}` | Append to file |
| PATCH | `/vault/{path}` | Patch file content |
| DELETE | `/vault/{path}` | Delete file |
| POST | `/search/simple/` | Text search |
| POST | `/search/` | JsonLogic/DQL search |
| GET | `/periodic/{period}/` | Get periodic note |
| GET | `/periodic/{period}/recent` | List recent periodic notes |

## Configuration

```mermaid
graph TD
    subgraph "Configuration Sources"
        Env["Environment Variables<br/>OBSIDIAN_API_KEY<br/>OBSIDIAN_HOST<br/>OBSIDIAN_PORT"]
        DotEnv[".env File"]
        MCPConfig["MCP Server Config<br/>claude_desktop_config.json"]
    end

    DotEnv -->|python-dotenv| Env
    MCPConfig -->|sets| Env
    Env -->|read by| Client["Obsidian Client"]
```

## Error Handling

```mermaid
graph TD
    Request["HTTP Request"]
    Request --> Success{Success?}
    Success -->|Yes| Parse["Parse Response"]
    Success -->|No| HTTPError["HTTPStatusError"]
    HTTPError --> ExtractError["Extract error code/message"]
    ExtractError --> RaiseEx["Raise Exception"]
    
    Request --> ConnError["Connection Error"]
    ConnError --> RaiseReq["Raise 'Request failed'"]
```

**Error Types:**
- `HTTPStatusError` - API returned error status (4xx, 5xx)
- `RequestError` - Connection/network failures

## Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| HTTP Client | httpx 0.28+ | HTTP/2 support, modern async-capable |
| CLI Framework | Click 8.0+ | Command parsing, help generation |
| MCP Protocol | mcp 1.1.0+ | AI assistant integration |
| Configuration | python-dotenv | .env file support |
| Type Checking | basedpyright | Static type analysis |
| Linting | ruff | Fast Python linter/formatter |
| Testing | pytest | Test framework |

## Package Structure

```
mcp-obsidian/
├── src/
│   ├── mcp_obsidian/           # MCP Server Package
│   │   ├── __init__.py         # Package entry, main()
│   │   ├── server.py           # MCP server setup
│   │   ├── tools.py            # 13 ToolHandler classes
│   │   └── obsidian.py         # HTTP/2 API client
│   │
│   └── cli_obsidian/           # CLI Package
│       ├── __init__.py         # Package entry, main()
│       ├── cli.py              # 11 Click commands
│       └── output.py           # Output formatting
│
├── tests/
│   └── cli_obsidian/           # CLI tests
│       └── test_cli.py         # 23 test cases
│
├── docs/
│   ├── api-reference.md        # Python API docs
│   ├── cli-reference.md        # CLI command docs
│   └── architecture.md         # This document
│
├── pyproject.toml              # Project configuration
└── README.md                   # Project overview
```
