
import requests
import json

BASE_URL = "http://localhost:8000/mcp"

def send_request(method, params=None, msg_id=1):
    payload = {
        "jsonrpc": "2.0",
        "id": msg_id,
        "method": method,
        "params": params or {}
    }
    resp = requests.post(BASE_URL, json=payload)
    print(f"→ Request: {method}")
    print(f"← Response: {json.dumps(resp.json(), indent=2)}\n")
    return resp.json()

if __name__ == "__main__":
    print("🧪 Testing MCP Server...\n")

    # Step 1: Initialize
    send_request("initialize", {"protocolVersion": "2023-10-26"}, msg_id=1)

    # Step 2: Notify initialized
    send_request("notifications/initialized", msg_id=None)  # notification has no id

    # Step 3: Call tools
    send_request("callTool", {"name": "get_current_time"}, msg_id=2)
    send_request("callTool", {"name": "echo", "arguments": {"message": "Hello MCP!"}}, msg_id=3)
