#!/usr/bin/env python3

import sys
from fastmcp import FastMCP

from .say_hello import say_hello_to_user


# Create MCP server
mcp = FastMCP("kgesh-kgesh-sam-hello-1-py")


@mcp.tool()
def say_hello(username: str) -> str:
    """Say hello to the user.
    
    Args:
        username: The name of the user to say hello to.
        
    Returns:
        A personalized greeting with environment information.
    """
    print(f"[TOOL CALL LOG] say_hello: username={username}", file=sys.stderr)
    
    if not username:
        print("[TOOL CALL ERROR] username is required", file=sys.stderr)
        raise ValueError("username is required")
    
    result = say_hello_to_user(username)
    return result


def main():
    """Main entry point."""
    mcp.run()