#!/usr/bin/env python3
"""
Simple test script for MCP Tools Server
Tests each tool to ensure they're working correctly
"""

import json
import subprocess
import sys
import time

def send_request(server_process, request):
    """Send a JSON-RPC request to the server"""
    request_json = json.dumps(request) + "\n"
    server_process.stdin.write(request_json.encode('utf-8'))
    server_process.stdin.flush()
    
    # Read response
    response_line = server_process.stdout.readline().decode('utf-8').strip()
    return json.loads(response_line) if response_line else None

def test_initialize(server_process):
    """Test initialization"""
    print("Testing initialize...")
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {}
    }
    response = send_request(server_process, request)
    if response and response.get("result"):
        print("✓ Initialize successful")
        print(f"  Server: {response['result'].get('serverInfo', {}).get('name')}")
        return True
    else:
        print("✗ Initialize failed")
        return False

def test_list_tools(server_process):
    """Test listing tools"""
    print("\nTesting tools/list...")
    request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list"
    }
    response = send_request(server_process, request)
    if response and response.get("result"):
        tools = response["result"].get("tools", [])
        print(f"✓ Found {len(tools)} tools:")
        for tool in tools:
            print(f"  - {tool.get('name')}: {tool.get('description')}")
        return True
    else:
        print("✗ tools/list failed")
        return False

def test_test_tool(server_process):
    """Test the test_tool"""
    print("\nTesting test_tool...")
    request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "test_tool",
            "arguments": {
                "message": "Hello from test script!"
            }
        }
    }
    response = send_request(server_process, request)
    if response and response.get("result"):
        print("✓ test_tool successful")
        content = response["result"].get("content", [{}])[0].get("text", "")
        print(f"  Response: {content[:100]}...")
        return True
    else:
        print("✗ test_tool failed")
        print(f"  Error: {response.get('error') if response else 'No response'}")
        return False

def test_web_search(server_process):
    """Test web search"""
    print("\nTesting web_search...")
    request = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "web_search",
            "arguments": {
                "query": "Python programming",
                "max_results": 3
            }
        }
    }
    response = send_request(server_process, request)
    if response and response.get("result"):
        print("✓ web_search successful")
        content = response["result"].get("content", [{}])[0].get("text", "")
        data = json.loads(content)
        if data.get("success"):
            results = data.get("data", {}).get("results", [])
            print(f"  Found {len(results)} results")
        return True
    else:
        print("✗ web_search failed")
        print(f"  Error: {response.get('error') if response else 'No response'}")
        return False

def test_fetch_webpage(server_process):
    """Test webpage fetching"""
    print("\nTesting fetch_webpage...")
    request = {
        "jsonrpc": "2.0",
        "id": 5,
        "method": "tools/call",
        "params": {
            "name": "fetch_webpage",
            "arguments": {
                "url": "https://example.com"
            }
        }
    }
    response = send_request(server_process, request)
    if response and response.get("result"):
        print("✓ fetch_webpage successful")
        content = response["result"].get("content", [{}])[0].get("text", "")
        data = json.loads(content)
        if data.get("success"):
            page_data = data.get("data", {})
            print(f"  Title: {page_data.get('title', 'N/A')}")
            print(f"  Status: {page_data.get('status_code', 'N/A')}")
        return True
    else:
        print("✗ fetch_webpage failed")
        print(f"  Error: {response.get('error') if response else 'No response'}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("MCP Tools Server Test Suite")
    print("=" * 50)
    
    # Start the server
    print("\nStarting MCP server...")
    server_process = subprocess.Popen(
        [sys.executable, "mcp-tools.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Give server a moment to start
    time.sleep(1)
    
    results = []
    
    try:
        # Run tests
        results.append(("Initialize", test_initialize(server_process)))
        results.append(("List Tools", test_list_tools(server_process)))
        results.append(("Test Tool", test_test_tool(server_process)))
        results.append(("Web Search", test_web_search(server_process)))
        results.append(("Fetch Webpage", test_fetch_webpage(server_process)))
        
    finally:
        # Clean up
        server_process.terminate()
        server_process.wait()
    
    # Print summary
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())

