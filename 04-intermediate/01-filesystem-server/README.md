# Filesystem MCP Server

A practical MCP server that gives AI models safe, controlled access to the local filesystem.

## Features

- Read files with size and type limits
- Write/create new files with validation
- List directory contents
- Search for files by name pattern
- Get file metadata (size, dates, permissions)
- Move and copy files
- **Security**: sandboxed to a configured base directory — no path traversal

## Run It

### Option 1: Inspector (Recommended for Testing)
```bash
cd 04-intermediate/01-filesystem-server
mcp dev filesystem_server.py
```

The `mcp dev` command will:
1. Install the MCP Inspector (npm) if needed
2. Start a proxy server on `localhost:6277`
3. Open the interactive inspector in your browser
4. Display all available file system tools

In the inspector:
- Test file operations (read, write, list)
- See sandboxing in action (can't escape working directory)
- View directory listings
- Test file operations with different paths
- Stop with `Ctrl+C`

### Option 2: Start as Server (Integration)
```bash
cd 04-intermediate/01-filesystem-server
python filesystem_server.py
```

This starts the server on stdio transport, ready for a client like Claude Desktop to connect.

## Security Notes

This server **sandbox** all file operations to a `BASE_DIR`:
- All paths are resolved and validated against `BASE_DIR`
- `../` path traversal attempts are blocked
- Only safe file extensions are readable/writable
- File size limits prevent memory exhaustion
