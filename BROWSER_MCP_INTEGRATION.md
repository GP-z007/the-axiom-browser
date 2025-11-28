# Axiom Browser - MCP Tools Integration

The Axiom Browser now integrates MCP (Model Context Protocol) tools for enhanced web searching and webpage fetching capabilities.

## Features

### 🔍 MCP-Powered Web Search
- When you enter a search query in the URL bar, the browser uses the `web_search` MCP tool
- Displays beautiful, formatted search results directly in the browser
- Results are fetched from DuckDuckGo using the MCP tool
- Shows instant answers when available

### 📄 MCP-Powered Webpage Fetching
- When you enter a URL, the browser uses the `fetch_webpage` MCP tool
- Fetches and displays webpage content directly
- Better error handling and status reporting

### 🎨 Modern UI
- Dark theme throughout
- Beautiful search results page with hover effects
- Real-time status updates
- Search button (🔍) for easy access

## Installation

### 1. Install Required Dependencies

```bash
# Activate your virtual environment (if using one)
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Install httpx for MCP tools
pip install httpx
```

### 2. Run the Browser

```bash
python web-browser.py
```

## How It Works

### Search with MCP Tools

1. **Enter a search query** in the URL bar (e.g., "Python programming")
2. Press **Enter** or click the **🔍 Search button**
3. The browser automatically:
   - Detects it's a search query (not a URL)
   - Calls the `web_search` MCP tool
   - Fetches results from DuckDuckGo
   - Displays formatted results in the browser

### Navigate with MCP Tools

1. **Enter a URL** in the URL bar (e.g., "example.com" or "https://example.com")
2. Press **Enter** or click the **🔍 Search button**
3. The browser automatically:
   - Detects it's a URL
   - Calls the `fetch_webpage` MCP tool
   - Fetches the webpage content
   - Displays it in the browser

## MCP Tools Used

### 1. web_search
- **Purpose**: Search the web for information
- **Input**: Search query string
- **Output**: Formatted search results with titles, URLs, and snippets
- **Source**: DuckDuckGo API and HTML search

### 2. fetch_webpage
- **Purpose**: Fetch webpage content
- **Input**: URL string
- **Output**: Webpage HTML content
- **Features**: Automatic protocol detection, error handling

## Architecture

### AsyncWorker Class
- Handles async MCP operations in a separate thread
- Prevents UI freezing during network requests
- Emits signals when operations complete

### MCPTools Class
- Contains all MCP tool implementations
- Handles web search and webpage fetching
- Creates beautiful HTML for search results

### Integration
- Seamlessly integrated into MainWindow
- Automatic detection of URLs vs search queries
- Fallback to regular navigation if MCP tools unavailable

## Status Indicators

- **✓ MCP Tools Enabled**: MCP tools are active and ready
- **⚠ MCP Tools Disabled**: httpx not installed, using fallback methods
- **"Searching with MCP tools..."**: Active search operation
- **"Fetching webpage with MCP tools..."**: Active fetch operation

## Troubleshooting

### MCP Tools Not Working

1. **Check httpx installation**:
   ```bash
   pip install httpx
   ```

2. **Verify installation**:
   ```python
   python -c "import httpx; print('httpx installed')"
   ```

3. **Restart the browser** after installing httpx

### Search Results Not Showing

- Check your internet connection
- Verify DuckDuckGo is accessible
- Check the status bar for error messages
- Browser will fallback to regular Google search if MCP fails

### Webpage Not Loading

- Verify the URL is correct
- Check if the website is accessible
- Browser will fallback to regular navigation if MCP fails

## Technical Details

### Async Operations
- Uses `QThread` for async operations
- Prevents blocking the UI thread
- Signals used for completion callbacks

### URL Detection
- Automatically detects URLs vs search queries
- Handles domains without protocols
- Smart query parsing

### Error Handling
- Graceful fallback to regular navigation
- User-friendly error messages
- Status bar notifications

## Future Enhancements

- [ ] Add more MCP tools (file operations, etc.)
- [ ] Cache search results
- [ ] Add search history
- [ ] Implement bookmark system
- [ ] Add tab support
- [ ] Custom search engines

## License

Part of the Axiom OS project.

