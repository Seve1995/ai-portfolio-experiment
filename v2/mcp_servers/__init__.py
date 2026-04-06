"""
MCP Tool Registry
Central registry of all available tools. Maps tool names to their implementations
and provides the tool definitions for LLM function calling.
"""

import logging
from typing import Any

from . import fred_server
from . import web_search_server
from . import url_fetch_server
from . import finnhub_news_server
from . import stock_data_server

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Tool Registry
# ─────────────────────────────────────────────

TOOLS = {
    "get_macro": {
        "definition": fred_server.TOOL_DEFINITION,
        "execute": fred_server.execute,
    },
    "web_search": {
        "definition": web_search_server.TOOL_DEFINITION,
        "execute": web_search_server.execute,
    },
    "fetch_url": {
        "definition": url_fetch_server.TOOL_DEFINITION,
        "execute": url_fetch_server.execute,
    },
    "get_market_news": {
        "definition": finnhub_news_server.TOOL_DEFINITION,
        "execute": finnhub_news_server.execute,
    },
    "get_technicals": {
        "definition": stock_data_server.TECHNICALS_TOOL,
        "execute": stock_data_server.get_technicals,
    },
    "get_fundamentals": {
        "definition": stock_data_server.FUNDAMENTALS_TOOL,
        "execute": stock_data_server.get_fundamentals,
    },
}


def get_tool_definitions() -> list[dict]:
    """Get all tool definitions formatted for LLM function calling."""
    return [tool["definition"] for tool in TOOLS.values()]


def execute_tool(tool_name: str, arguments: dict[str, Any]) -> dict:
    """
    Execute a tool by name with the given arguments.
    
    Args:
        tool_name: Name of the tool to execute
        arguments: Tool arguments as a dict
        
    Returns:
        Tool result as a dict
    """
    if tool_name not in TOOLS:
        return {"error": f"Unknown tool: {tool_name}. Available: {list(TOOLS.keys())}"}

    tool = TOOLS[tool_name]
    try:
        result = tool["execute"](**arguments)
        logger.info(f"Tool {tool_name} executed successfully")
        return result
    except TypeError as e:
        logger.error(f"Tool {tool_name} argument error: {e}")
        return {"error": f"Invalid arguments for {tool_name}: {e}"}
    except Exception as e:
        logger.error(f"Tool {tool_name} execution error: {e}")
        return {"error": f"Tool {tool_name} failed: {e}"}
