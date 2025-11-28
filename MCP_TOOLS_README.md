# MCP Tools Server for Ollama Integration

A Model Context Protocol (MCP) server implementation providing web search, webpage fetching, and testing tools for Ollama integration.

## Features

- **web_search**: Search the web for information
- **fetch_webpage**: Fetch and retrieve webpage content
- **test_tool**: Simple echo/test tool for verification

## Installation

### 1. Install Required Libraries

```bash
# Activate your virtual environment first (if using one)
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows

# Install required packages
pip install -r requirements-mcp.txt
```

### 2. Make the script executable (optional)

```bash
chmod +x mcp-tools.py
```

## Required Libraries

The following libraries are required:

- **httpx** - Modern HTTP client for async requests
- **beautifulsoup4** (optional) - For better HTML parsing
- **lxml** (optional) - HTML parser backend

### Installation Commands

```bash
# Install core dependencies
pip install httpx

# Install optional dependencies for better HTML parsing
pip install beautifulsoup4 lxml

# Or install all at once
pip install httpx beautifulsoup4 lxml
```

## Usage

### Running the MCP Server

The server runs on stdio for integration with Ollama:

```bash
python mcp-tools.py
```

### Integration with Ollama

To use with Ollama, configure it as an MCP server. The server communicates via JSON-RPC over stdio.

### Testing the Tools

You can test the server manually by sending JSON-RPC requests:

**1. List available tools:**
```json
{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}
```

**2. Call web_search:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "web_search",
    "arguments": {
      "query": "Python async programming",
      "max_results": 5
    }
  }
}
```

**3. Call fetch_webpage:**
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "fetch_webpage",
    "arguments": {
      "url": "https://example.com"
    }
  }
}
```

**4. Call test_tool:**
```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "tools/call",
  "params": {
    "name": "test_tool",
    "arguments": {
      "message": "Hello from MCP!"
    }
  }
}
```

## Tool Definitions

### web_search

Searches the web for information.

**Parameters:**
- `query` (required): Search query string
- `max_results` (optional): Maximum number of results (default: 5)

**Returns:**
- Search results with titles, snippets, and URLs

### fetch_webpage

Fetches and parses webpage content.

**Parameters:**
- `url` (required): URL of the webpage to fetch

**Returns:**
- Page title, content preview, status code, and content length

### test_tool

Simple test tool that echoes back input.

**Parameters:**
- `message` (required): Message to echo back

**Returns:**
- Echoed message with timestamp

## Configuration

The server uses standard logging. Adjust log levels in the script:

```python
logging.basicConfig(level=logging.INFO)  # Change to DEBUG for more details
```

## Troubleshooting

1. **Import errors**: Make sure all dependencies are installed
   ```bash
   pip install httpx beautifulsoup4 lxml
   ```

2. **Stdio issues**: Ensure the script is run directly, not redirected
   ```bash
   python mcp-tools.py  # Correct
   python mcp-tools.py > output.txt  # May cause issues
   ```

3. **Connection errors**: Check your internet connection for web_search and fetch_webpage

## License

Part of the Axiom OS project.

