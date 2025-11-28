import sys
import json
import re
import asyncio
from urllib.parse import quote
from typing import Dict, Any
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
try:
    import httpx
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("Warning: httpx not installed. MCP tools disabled. Install with: pip install httpx")


class ModernButton(QPushButton):
    def __init__(self, icon_text, tooltip, parent=None):
        super().__init__(icon_text, parent)
        self.setToolTip(tooltip)
        self.setFixedSize(40, 40)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                border: none;
                border-radius: 8px;
                font-size: 18px;
                font-weight: bold;
                color: #e0e0e0;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
            QPushButton:pressed {
                background-color: #2a2a2a;
            }
        """)


class MCPTools:
    """MCP Tools for web search and webpage fetching"""
    
    def __init__(self):
        self.enabled = MCP_AVAILABLE
    
    async def web_search(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """Search the web using DuckDuckGo"""
        if not self.enabled:
            return {"success": False, "error": "MCP tools not available"}
        
        try:
            results = []
            
            # Try DuckDuckGo Instant Answer API first
            instant_url = f"https://api.duckduckgo.com/?q={quote(query)}&format=json&no_html=1&skip_disambig=1"
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                try:
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
                except:
                    pass
                
                # Get regular search results
                search_url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
                response = await client.get(search_url, follow_redirects=True)
                response.raise_for_status()
                
                html_content = response.text
                result_pattern = r'<a class="result__a".*?href="([^"]+)".*?>(.*?)</a>'
                matches = re.findall(result_pattern, html_content, re.DOTALL)
                
                for url, title_html in matches[:max_results]:
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
                
                if not results:
                    results.append({
                        "title": f"Search results for: {query}",
                        "snippet": f"Please visit DuckDuckGo to see full results",
                        "url": f"https://duckduckgo.com/?q={quote(query)}",
                        "source": "DuckDuckGo"
                    })
                
                return {
                    "success": True,
                    "data": {
                        "query": query,
                        "results": results[:max_results],
                        "total_results": len(results)
                    }
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def fetch_webpage(self, url: str) -> Dict[str, Any]:
        """Fetch webpage content"""
        if not self.enabled:
            return {"success": False, "error": "MCP tools not available"}
        
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                content = response.text
                
                title_start = content.find('<title>')
                title_end = content.find('</title>')
                title = content[title_start+7:title_end] if title_start != -1 else "No title"
                
                return {
                    "success": True,
                    "data": {
                        "url": url,
                        "status_code": response.status_code,
                        "title": title.strip(),
                        "content": content,
                        "content_length": len(content)
                    }
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_search_results_html(self, search_data: Dict[str, Any]) -> str:
        """Create HTML page for search results"""
        if not search_data.get("success"):
            return f"""
            <html>
            <head>
                <title>Search Error - Axiom Browser</title>
                <style>
                    body {{ background: #1e1e1e; color: #e0e0e0; font-family: Arial; padding: 20px; }}
                    .error {{ color: #ff6b6b; }}
                </style>
            </head>
            <body>
                <h1>Search Error</h1>
                <p class="error">{search_data.get('error', 'Unknown error')}</p>
            </body>
            </html>
            """
        
        data = search_data.get("data", {})
        query = data.get("query", "")
        results = data.get("results", [])
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Search: {query} - Axiom Browser</title>
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ 
                    background: #1e1e1e; 
                    color: #e0e0e0; 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                    padding: 20px;
                }}
                .header {{
                    margin-bottom: 30px;
                    padding-bottom: 20px;
                    border-bottom: 2px solid #404040;
                }}
                .header h1 {{
                    color: #5a90e2;
                    font-size: 24px;
                    margin-bottom: 10px;
                }}
                .query {{
                    color: #b0b0b0;
                    font-size: 14px;
                }}
                .result {{
                    background: #2d2d2d;
                    border-radius: 8px;
                    padding: 20px;
                    margin-bottom: 20px;
                    border: 1px solid #404040;
                    transition: all 0.3s;
                }}
                .result:hover {{
                    background: #353535;
                    border-color: #5a90e2;
                    transform: translateX(5px);
                }}
                .result-title {{
                    color: #5a90e2;
                    font-size: 20px;
                    margin-bottom: 10px;
                    text-decoration: none;
                    display: block;
                }}
                .result-title:hover {{
                    text-decoration: underline;
                }}
                .result-url {{
                    color: #4CAF50;
                    font-size: 14px;
                    margin-bottom: 10px;
                    word-break: break-all;
                }}
                .result-snippet {{
                    color: #b0b0b0;
                    line-height: 1.6;
                    margin-bottom: 10px;
                }}
                .result-source {{
                    color: #888;
                    font-size: 12px;
                    font-style: italic;
                }}
                .stats {{
                    color: #888;
                    font-size: 14px;
                    margin-bottom: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🔍 Search Results</h1>
                <div class="query">Query: <strong>{query}</strong></div>
                <div class="stats">Found {len(results)} result(s)</div>
            </div>
        """
        
        for result in results:
            title = result.get("title", "No title")
            url = result.get("url", "#")
            snippet = result.get("snippet", "No description available")
            source = result.get("source", "")
            
            html += f"""
            <div class="result">
                <a href="{url}" class="result-title" target="_blank">{title}</a>
                <div class="result-url">{url}</div>
                <div class="result-snippet">{snippet}</div>
                <div class="result-source">{source}</div>
            </div>
            """
        
        html += """
        </body>
        </html>
        """
        
        return html


class AsyncWorker(QThread):
    """Worker thread for async MCP operations"""
    finished = pyqtSignal(dict)
    
    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(self.func(*self.args, **self.kwargs))
            self.finished.emit(result)
        finally:
            loop.close()


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        
        # Initialize MCP Tools
        self.mcp_tools = MCPTools()
        self.current_worker = None
        
        # Set window properties
        self.setWindowTitle("Axiom Browser - Powered by MCP Tools")
        self.setMinimumSize(1200, 800)
        
        # Apply modern dark theme styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                color: #e0e0e0;
            }
            QToolBar {
                background-color: #2d2d2d;
                border: none;
                border-bottom: 1px solid #404040;
                spacing: 10px;
                padding: 10px;
            }
            QLineEdit {
                background-color: #353535;
                border: 2px solid #404040;
                border-radius: 20px;
                padding: 8px 15px;
                font-size: 14px;
                color: #e0e0e0;
                selection-background-color: #5a90e2;
            }
            QLineEdit:focus {
                border: 2px solid #5a90e2;
                background-color: #3a3a3a;
            }
        """)
        
        # Create browser view
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl('https://google.com'))
        self.setCentralWidget(self.browser)
        self.showMaximized()

        # Create modern navbar
        navbar = QToolBar()
        navbar.setMovable(False)
        navbar.setStyleSheet("""
            QToolBar {
                background-color: #2d2d2d;
                border: none;
                border-bottom: 1px solid #404040;
                spacing: 10px;
                padding: 10px 15px;
            }
        """)
        self.addToolBar(navbar)

        # Navigation buttons with modern icons
        back_btn = ModernButton("🔙", "Back")
        back_btn.clicked.connect(self.browser.back)
        navbar.addWidget(back_btn)

        forward_btn = ModernButton("🔜", "Forward")
        forward_btn.clicked.connect(self.browser.forward)
        navbar.addWidget(forward_btn)

        reload_btn = ModernButton("🔄", "Reload")
        reload_btn.clicked.connect(self.browser.reload)
        navbar.addWidget(reload_btn)

        home_btn = ModernButton("🏠", "Home")
        home_btn.clicked.connect(self.navigate_home)
        navbar.addWidget(home_btn)

        # Add spacer
        navbar.addSeparator()

        # Modern URL bar with dark theme styling
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Enter URL or search with MCP tools...")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.url_bar.setStyleSheet("""
            QLineEdit {
                background-color: #353535;
                border: 2px solid #404040;
                border-radius: 25px;
                padding: 10px 20px;
                font-size: 14px;
                color: #e0e0e0;
                min-height: 20px;
            }
            QLineEdit:focus {
                border: 2px solid #5a90e2;
                background-color: #3a3a3a;
            }
            QLineEdit::placeholder {
                color: #888888;
            }
        """)
        navbar.addWidget(self.url_bar)
        
        # Search/Go button
        search_btn = ModernButton("🔍", "Search/Go")
        search_btn.clicked.connect(self.navigate_to_url)
        navbar.addWidget(search_btn)

        # Connect URL changes
        self.browser.urlChanged.connect(self.update_url)
        self.browser.loadProgress.connect(self.update_progress)

        # Create status bar for loading progress with dark theme
        self.statusBar().setStyleSheet("""
            QStatusBar {
                background-color: #2d2d2d;
                border-top: 1px solid #404040;
                color: #b0b0b0;
            }
        """)
        
        # Show MCP status
        if self.mcp_tools.enabled:
            self.statusBar().showMessage("✓ MCP Tools Enabled - Powered by Axiom Browser", 5000)
        else:
            self.statusBar().showMessage("⚠ MCP Tools Disabled - Install httpx: pip install httpx", 5000)

    def navigate_home(self):
        self.browser.setUrl(QUrl('https://google.com'))

    def navigate_to_url(self):
        input_text = self.url_bar.text().strip()
        
        if not input_text:
            return
        
        # Check if it's a URL or search query
        is_url = False
        
        if input_text.startswith(('http://', 'https://')):
            is_url = True
        elif '.' in input_text and ' ' not in input_text and not any(char in input_text for char in ['?', '&']):
            # Looks like a domain
            is_url = True
        
        if is_url:
            # Use fetch_webpage MCP tool
            if not input_text.startswith(('http://', 'https://')):
                input_text = 'https://' + input_text
            self.statusBar().showMessage("Fetching webpage with MCP tools...")
            self.fetch_with_mcp(input_text)
        else:
            # Use web_search MCP tool
            self.statusBar().showMessage("Searching with MCP tools...")
            self.search_with_mcp(input_text)
    
    def search_with_mcp(self, query: str):
        """Use MCP web_search tool and display results"""
        if not self.mcp_tools.enabled:
            # Fallback to regular search
            url = f"https://www.google.com/search?q={quote(query)}"
            self.browser.setUrl(QUrl(url))
            return
        
        # Cancel any existing worker
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.terminate()
        
        # Create worker for async operation
        self.current_worker = AsyncWorker(self.mcp_tools.web_search, query, 10)
        self.current_worker.finished.connect(self.on_search_complete)
        self.current_worker.start()
    
    def fetch_with_mcp(self, url: str):
        """Use MCP fetch_webpage tool"""
        if not self.mcp_tools.enabled:
            # Fallback to regular navigation
            self.browser.setUrl(QUrl(url))
            return
        
        # Cancel any existing worker
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.terminate()
        
        # Create worker for async operation
        self.current_worker = AsyncWorker(self.mcp_tools.fetch_webpage, url)
        self.current_worker.finished.connect(self.on_fetch_complete)
        self.current_worker.start()
    
    def on_search_complete(self, result: dict):
        """Handle search results from MCP tool"""
        self.statusBar().clearMessage()
        
        if result.get("success"):
            # Create HTML page with search results
            html = self.mcp_tools.create_search_results_html(result)
            
            # Load HTML content into browser
            self.browser.setHtml(html, QUrl("about:blank"))
            
            # Update URL bar to show search query
            query = result.get("data", {}).get("query", "")
            self.url_bar.setText(f"axiom://search?q={quote(query)}")
            
            self.statusBar().showMessage(f"Search completed: {len(result.get('data', {}).get('results', []))} results", 3000)
        else:
            error_msg = result.get("error", "Unknown error")
            self.statusBar().showMessage(f"Search failed: {error_msg}", 5000)
            # Fallback to regular search
            query = self.url_bar.text()
            url = f"https://www.google.com/search?q={quote(query)}"
            self.browser.setUrl(QUrl(url))
    
    def on_fetch_complete(self, result: dict):
        """Handle webpage fetch from MCP tool"""
        self.statusBar().clearMessage()
        
        if result.get("success"):
            data = result.get("data", {})
            url = data.get("url", "")
            content = data.get("content", "")
            
            # Load the webpage content directly
            self.browser.setHtml(content, QUrl(url))
            self.url_bar.setText(url)
            self.statusBar().showMessage(f"Page loaded: {data.get('title', 'Unknown')}", 3000)
        else:
            error_msg = result.get("error", "Unknown error")
            self.statusBar().showMessage(f"Fetch failed: {error_msg}", 5000)
            # Fallback to regular navigation
            url = self.url_bar.text()
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            self.browser.setUrl(QUrl(url))

    def update_url(self, q):
        url_str = q.toString()
        # Don't update URL bar if it's an internal search result page
        if not url_str.startswith("axiom://"):
            self.url_bar.setText(url_str)

    def update_progress(self, progress):
        if progress < 100:
            self.statusBar().showMessage(f"Loading... {progress}%")
        else:
            self.statusBar().clearMessage()


app = QApplication(sys.argv)
QApplication.setApplicationName('Axiom Browser')
window = MainWindow()
app.exec_()