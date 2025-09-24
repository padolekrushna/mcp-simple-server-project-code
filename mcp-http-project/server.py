
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from datetime import datetime
from typing import List, Dict, Any

app = FastAPI(title="Simple MCP Server", description="A minimal MCP server over HTTP")

# Store initialized state
initialized = False

@app.post("/mcp")
async def mcp_endpoint(request: Request):
    global initialized
    body = await request.json()
    method = body.get("method")
    msg_id = body.get("id")

    if method == "initialize":
        # Confirm protocol and advertise tools
        initialized = True
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2023-10-26",
                "capabilities": {
                    "tools": [
                        {
                            "name": "get_current_time",
                            "description": "Returns the current date and time in ISO format.",
                            "inputSchema": {"type": "object", "properties": {}, "required": []}
                        },
                        {
                            "name": "echo",
                            "description": "Echoes back the input message.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {"message": {"type": "string"}},
                                "required": ["message"]
                            }
                        }
                    ]
                }
            }
        })

    elif method == "callTool":
        tool_name = body["params"]["name"]
        args = body["params"].get("arguments", {})

        if tool_name == "get_current_time":
            now = datetime.now().isoformat()
            content = [{"type": "text", "text": f"Current time: {now}"}]

        elif tool_name == "echo":
            msg = args.get("message", "no message")
            content = [{"type": "text", "text": f"You said: {msg}"}]

        else:
            content = [{"type": "text", "text": f"Tool '{tool_name}' not found."}]
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"content": content, "isError": True}
            })

        return JSONResponse({
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {"content": content, "isError": False}
        })

    elif method == "notifications/initialized":
        # Client notifies that it's done initializing
        return JSONResponse({})

    # Unknown method
    return JSONResponse({"jsonrpc": "2.0", "error": {"code": -32601, "message": "Method not found"}})