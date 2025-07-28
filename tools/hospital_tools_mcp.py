import sys
import json
import asyncio
import requests

from mcp.server.fastmcp import FastMCP

# The URL of our actual ROS2-MCP bridge
ROS_MCP_BRIDGE_URL = "http://127.0.0.1:8081/execute_tool"

# --- Tool Implementations ---

# Initialize FastMCP server
# Give it a unique name to distinguish it from your other "robots" server
mcp = FastMCP("hospital-tools")

@mcp.tool()
async def guide_patient_to_room(room_number: str) -> str:
    """
    Guides a person from the current location to a specified room number.
    This makes an API call to the ROS2 bridge to navigate the robot.
    
    Args:
        room_number: The room number to navigate to.
    """
    try:
        response = requests.post(
            ROS_MCP_BRIDGE_URL,
            json={"tool_name": "guide_patient_to_room", "args": {"room_number": room_number}},
        )
        response.raise_for_status()
        return f"Successfully dispatched navigation task for room {room_number}."
    except requests.exceptions.RequestException as e:
        return f"Failed to call ROS bridge: {e}"

@mcp.tool()
async def speak(message: str) -> str:
    """
    Speaks a given message out loud.
    This makes an API call to the ROS2 bridge to make the robot speak.

    Args:
        message: The message for the robot to say.
    """
    try:
        response = requests.post(
            ROS_MCP_BRIDGE_URL,
            json={"tool_name": "speak", "args": {"message": message}},
        )
        response.raise_for_status()
        return f"Successfully dispatched speak task."
    except requests.exceptions.RequestException as e:
        return f"Failed to call ROS bridge: {e}"

# --- Manual MCP-like Server ---

async def handle_request(request_data, tools):
    method = request_data.get("method")
    params = request_data.get("params", {})
    request_id = request_data.get("id")

    if method == "initialize":
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2.0",
                "serverInfo": {
                    "name": "Hospital-Tool-Server",
                    "version": "1.0.0"
                },
                "capabilities": {}
            },
        }
    elif method == "list_tools":
        response = {"jsonrpc": "2.0", "id": request_id, "result": {"tools": list(tools.values())}}
    elif method == "execute_tool":
        tool_name = params.get("name")
        tool_input = params.get("input", {})
        if tool_name in tools:
            try:
                # This is a simplified implementation. A real one would handle args better.
                # Assuming single argument for our tools.
                arg_value = list(tool_input.values())[0]
                if tool_name == "guide_patient_to_room":
                    result = await guide_patient_to_room(arg_value)
                elif tool_name == "speak":
                    result = await speak(arg_value)
                else:
                    result = "Unknown tool"
                
                response = {"jsonrpc": "2.0", "id": request_id, "result": {"output": result}}
            except Exception as e:
                response = {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32603, "message": str(e)}}
        else:
            response = {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32601, "message": "Tool not found"}}
    else:
        response = {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32601, "message": "Method not found"}}
    
    return response

async def main():
    tools = {
        "guide_patient_to_room": {
            "name": "guide_patient_to_room",
            "description": "Guides a person from the current location to a specified room number.",
            "inputSchema": {"type": "object", "properties": {"room_number": {"type": "string"}}},
        },
        "speak": {
            "name": "speak",
            "description": "Speaks a given message out loud.",
            "inputSchema": {"type": "object", "properties": {"message": {"type": "string"}}},
        },
    }

    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await asyncio.get_event_loop().connect_read_pipe(lambda: protocol, sys.stdin)

    writer_transport, writer_protocol = await asyncio.get_event_loop().connect_write_pipe(
        asyncio.streams.FlowControlMixin, sys.stdout
    )
    writer = asyncio.StreamWriter(writer_transport, writer_protocol, None, asyncio.get_event_loop())

    while not reader.at_eof():
        line = await reader.readline()
        if not line:
            break
        try:
            request_data = json.loads(line)
            response = await handle_request(request_data, tools)
            writer.write(json.dumps(response).encode() + b'\n')
            await writer.drain()
        except json.JSONDecodeError:
            # Ignore non-json lines
            pass

if __name__ == "__main__":
    # Initialize and run the server using the standard mcp runner
    # This will handle all the stdio communication and protocol details.
    mcp.run(transport="stdio")
    
    # asyncio.run(main())
    