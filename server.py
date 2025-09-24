# server.py
import logging
from datetime import datetime
from typing import Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define MCP request structure for FastAPI docs
class MCPRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[int] = None
    method: str
    params: dict[str, Any]

app = FastAPI(title="Simple MCP Server", description="Minimal MCP server over HTTP")

initialized = False

# Root endpoint for Azure (shows friendly message)
@app.get("/")
def home():
    return {
        "status": "MCP Server is running!",
        "mcp_endpoint": "/mcp",
        "docs": "/docs",
        "usage": "Send POST requests to /mcp with MCP JSON-RPC format"
    }

# Main MCP endpoint with typed request
@app.post("/mcp")
async def mcp_endpoint(request: MCPRequest):
    global initialized
    logger.info(f"🟩 Received MCP request: method={request.method}, id={request.id}")
    
    method = request.method
    msg_id = request.id
    params = request.params

    if method == "initialize":
        logger.info("🚀 Handling 'initialize'")
        initialized = True
        response = {
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
        }
        logger.info("✅ Sending initialize response")
        return JSONResponse(response)

    elif method == "callTool":
        logger.info("🛠️ Handling 'callTool'")
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if tool_name == "get_current_time":
            now = datetime.now().isoformat()
            content = [{"type": "text", "text": f"Current time: {now}"}]
            logger.info(f"🕒 Time tool result: {now}")

        elif tool_name == "echo":
            msg = arguments.get("message", "no message")
            content = [{"type": "text", "text": f"You said: {msg}"}]
            logger.info(f"🔁 Echo tool result: {msg}")

        else:
            logger.warning(f"⚠️ Unknown tool: {tool_name}")
            content = [{"type": "text", "text": f"Tool '{tool_name}' not found."}]
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"content": content, "isError": True}
            })

        response = {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {"content": content, "isError": False}
        }
        logger.info("✅ Sending tool response")
        return JSONResponse(response)

    elif method == "notifications/initialized":
        logger.info("🔔 Received 'notifications/initialized'")
        return JSONResponse({})

    else:
        logger.warning(f"❓ Unknown method: {method}")
        return JSONResponse({
            "jsonrpc": "2.0",
            "error": {"code": -32601, "message": "Method not found"}
        })
