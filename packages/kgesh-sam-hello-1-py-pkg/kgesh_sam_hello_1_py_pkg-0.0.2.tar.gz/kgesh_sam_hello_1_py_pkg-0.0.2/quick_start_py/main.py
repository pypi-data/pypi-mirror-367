#!/usr/bin/env python3

import sys
from typing import Annotated
from fastmcp import FastMCP

from .say_hello import say_hello_to_user
from .env import ENV


# Create MCP server with proper name and description
mcp = FastMCP(
    name="kgesh-sam-hello-1-py-pkg",
    version="0.0.1"
)


@mcp.tool
def say_hello(username: Annotated[str, "The name of the user to say hello to"]) -> str:
    """Say hello to the user with environment information.
    
    This tool greets a user by name and provides information about the 
    current environment including region, country, and command line arguments.
    
    Args:
        username: The name of the user to greet
        
    Returns:
        A personalized greeting message with environment details
    """
    # Log the tool call for debugging (visible in Deploxy dashboard)
    print(f"[TOOL CALL LOG] say_hello called with username: {username}", file=sys.stderr)
    
    if not username or not username.strip():
        print("[TOOL CALL ERROR] username is required and cannot be empty", file=sys.stderr)
        raise ValueError("Username is required and cannot be empty")
    
    try:
        result = say_hello_to_user(username.strip())
        return result
    except Exception as e:
        print(f"[TOOL CALL ERROR] Failed to generate greeting: {e}", file=sys.stderr)
        raise


@mcp.resource("env://info")
def get_environment_info():
    """Get current environment information.
    
    Returns environment variables injected by Deploxy for debugging.
    """
    return {
        "serverless_function_region": ENV.get("SERVERLESS_FUNCTION_REGION"),
        "user_request_country": ENV.get("USER_REQUEST_COUNTRY"), 
        "sample_env": ENV.get("SAMPLE_ENV"),
        "command_args": sys.argv[1:] if len(sys.argv) > 1 else []
    }


@mcp.prompt
def greeting_prompt(context: str = "formal") -> str:
    """Generate a greeting prompt template.
    
    Args:
        context: The context for the greeting (formal, casual, friendly)
        
    Returns:
        A formatted prompt for generating greetings
    """
    contexts = {
        "formal": "Please provide a professional and respectful greeting.",
        "casual": "Please provide a friendly and relaxed greeting.",
        "friendly": "Please provide a warm and welcoming greeting."
    }
    
    base_prompt = contexts.get(context, contexts["friendly"])
    return f"{base_prompt} Include the user's name and make it personalized."


def main():
    """Main entry point for the MCP server.
    
    Starts the FastMCP server using stdio transport (default).
    This is compatible with MCP clients and Deploxy deployment.
    """
    # Run with stdio transport (default for MCP)
    # This handles stdin/stdout communication with MCP clients
    mcp.run()


if __name__ == "__main__":
    main()