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

```bash
cd 04-intermediate/01-filesystem-server
python filesystem_server.py

# Or with MCP inspector:
mcp dev filesystem_server.py
```

## Security Notes

This server **sandbox** all file operations to a `BASE_DIR`:
- All paths are resolved and validated against `BASE_DIR`
- `../` path traversal attempts are blocked
- Only safe file extensions are readable/writable
- File size limits prevent memory exhaustion
