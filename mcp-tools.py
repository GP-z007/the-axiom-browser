#!/usr/bin/env python3
"""
MCP Tools Server for Ollama Integration
Implements web_search, fetch_webpage, and test_tool
"""

import sys
import json
import asyncio
import logging
from typing import Any, Dict, List, Optional
import httpx
from urllib.parse import quote

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MCPServer:
    """MCP Server implementation for tool execution"""
    
    def __init__(self):
        self.tools = {
            "web_search": {
                "name": "web_search",
                "description": "Search the web for information using a search query",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query to look up on the web"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of results to return (default: 5)",
                            "default": 5
                        }
                    },
                    "required": ["query"]
                }
            },
            "fetch_webpage": {
                "name": "fetch_webpage",
                "description": "Fetch and retrieve the content of a webpage",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "The URL of the webpage to fetch"
                        }
                    },
                    "required": ["url"]
                }
            },
            "test_tool": {
                "name": "test_tool",
                "description": "A simple test tool that echoes back the input",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "The message to echo back"
                        }
                    },
                    "required": ["message"]
                }
            }
        }
        
    async def web_search(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """
        Search the web using DuckDuckGo
        Uses DuckDuckGo Instant Answer API and HTML search
        """
        try:
            logger.info(f"Searching web for: {query} (max_results: {max_results})")
            
            results = []
            
            # Try DuckDuckGo Instant Answer API first
            instant_url = f"https://api.duckduckgo.com/?q={quote(query)}&format=json&no_html=1&skip_disambig=1"
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                try:
                    # Get instant answer
                    instant_response = await client.get(instant_url)
                    if instant_response.status_code == 200:
                        instant_data = instant_response.json()
                        if instant_data.get("AbstractText"):
                            results.append({
                                "title": instant_data.get("Heading", query),
                                "snippet": instant_data.get("AbstractText", ""),
                                "url": instant_data.get("AbstractURL", ""),
                                "source": "DuckDuckGo Instant Answer"
                            })
                except Exception as e:
                    logger.debug(f"Instant answer not available: {e}")
                
                # Get regular search results
                search_url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
                response = await client.get(search_url, follow_redirects=True)
                response.raise_for_status()
                
                # Extract results from HTML (simplified)
                html_content = response.text
                import re
                
                # Simple pattern matching for search results
                # In production, use BeautifulSoup for better parsing
                result_pattern = r'<a class="result__a".*?href="([^"]+)".*?>(.*?)</a>'
                matches = re.findall(result_pattern, html_content, re.DOTALL)
                
                for url, title_html in matches[:max_results]:
                    # Clean HTML tags from title
                    title = re.sub('<[^<]+?>', '', title_html).strip()
                    if title and url:
                        results.append({
                            "title": title[:200],
                            "snippet": f"Search result for: {query}",
                            "url": url,
                            "source": "DuckDuckGo Search"
                        })
                        if len(results) >= max_results:
                            break
                
                # If no results found, create a basic result
                if not results:
                    results.append({
                        "title": f"Search results for: {query}",
                        "snippet": f"Please visit DuckDuckGo to see full results for '{query}'",
                        "url": f"https://duckduckgo.com/?q={quote(query)}",
                        "source": "DuckDuckGo"
                    })
                
                logger.info(f"Search completed: {len(results)} results found")
                return {
                    "success": True,
                    "data": {
                        "query": query,
                        "results": results[:max_results],
                        "total_results": len(results)
                    }
                }
                
        except Exception as e:
            logger.error(f"Web search error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "data": {
                    "query": query,
                    "results": [],
                    "total_results": 0
                }
            }
    
    async def fetch_webpage(self, url: str) -> Dict[str, Any]:
        """Fetch the content of a webpage"""
        try:
            logger.info(f"Fetching webpage: {url}")
            
            # Add protocol if missing
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                content = response.text
                
                # Extract basic information
                title_start = content.find('<title>')
                title_end = content.find('</title>')
                title = content[title_start+7:title_end] if title_start != -1 else "No title found"
                
                # Extract text content (simplified - remove HTML tags)
                import re
                text_content = re.sub('<[^<]+?>', '', content)
                text_content = ' '.join(text_content.split())[:2000]  # Limit and clean
                
                result = {
                    "url": url,
                    "status_code": response.status_code,
                    "title": title.strip(),
                    "content_preview": text_content,
                    "content_length": len(content)
                }
                
                logger.info(f"Webpage fetched successfully: {url}")
                return {
                    "success": True,
                    "data": result
                }
                
        except Exception as e:
            logger.error(f"Fetch webpage error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def test_tool(self, message: str) -> Dict[str, Any]:
        """Simple test tool that echoes back the input"""
        logger.info(f"Test tool called with message: {message}")
        return {
            "success": True,
            "data": {
                "echo": message,
                "timestamp": asyncio.get_event_loop().time(),
                "status": "success"
            }
        }
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP requests"""
        method = request.get("method")
        request_id = request.get("id")
        
        try:
            if method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": list(self.tools.values())
                    }
                }
            
            elif method == "tools/call":
                tool_name = request.get("params", {}).get("name")
                arguments = request.get("params", {}).get("arguments", {})
                
                if tool_name == "web_search":
                    query = arguments.get("query")
                    max_results = arguments.get("max_results", 5)
                    result = await self.web_search(query, max_results)
                    
                elif tool_name == "fetch_webpage":
                    url = arguments.get("url")
                    result = await self.fetch_webpage(url)
                    
                elif tool_name == "test_tool":
                    message = arguments.get("message")
                    result = await self.test_tool(message)
                    
                else:
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32601,
                            "message": f"Unknown tool: {tool_name}"
                        }
                    }
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result, indent=2)
                            }
                        ]
                    }
                }
            
            elif method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "axiom-mcp-tools",
                            "version": "1.0.0"
                        }
                    }
                }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Unknown method: {method}"
                    }
                }
                
        except Exception as e:
            logger.error(f"Error handling request: {str(e)}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    async def run_stdio(self):
        """Run the MCP server on stdio for Ollama integration"""
        logger.info("Starting MCP server on stdio...")
        
        # Create async stdin reader
        loop = asyncio.get_event_loop()
        
        try:
            while True:
                # Read line from stdin asynchronously
                line = await loop.run_in_executor(None, sys.stdin.readline)
                if not line:
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                try:
                    request = json.loads(line)
                    logger.debug(f"Received request: {json.dumps(request, indent=2)}")
                    
                    response = await self.handle_request(request)
                    
                    response_json = json.dumps(response) + "\n"
                    await loop.run_in_executor(None, lambda: sys.stdout.write(response_json) or sys.stdout.flush())
                    
                    logger.debug(f"Sent response: {json.dumps(response, indent=2)}")
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON: {e}")
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32700,
                            "message": f"Parse error: {str(e)}"
                        }
                    }
                    error_json = json.dumps(error_response) + "\n"
                    await loop.run_in_executor(None, lambda: sys.stdout.write(error_json) or sys.stdout.flush())
                    
        except KeyboardInterrupt:
            logger.info("Shutting down MCP server...")
        except Exception as e:
            logger.error(f"Server error: {str(e)}", exc_info=True)


async def main():
    """Main entry point"""
    server = MCPServer()
    await server.run_stdio()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)

