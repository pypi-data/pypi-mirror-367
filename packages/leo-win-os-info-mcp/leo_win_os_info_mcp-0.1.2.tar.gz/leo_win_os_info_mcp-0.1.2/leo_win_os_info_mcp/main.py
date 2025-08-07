# main.py
from mcp.server.fastmcp import FastMCP
import platform
import json


def get_host_info() -> str:
    """get host information
    Returns:
        str: the host information in JSON string
    """
    info: dict[str, str] = {
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "processor": platform.processor(),
    }

    return json.dumps(info, indent=4)


mcp = FastMCP("host info mcp")
mcp.add_tool(get_host_info)


def main():
    mcp.run("stdio")


if __name__ == "__main__":
    main()
