"""Register Lightdash tools with the MCP server"""

import logging
from typing import List, TYPE_CHECKING, Any

from dbt_mcp.config.config import LightdashConfig
from dbt_mcp.tools.tool_names import ToolName

if TYPE_CHECKING:
    from dbt_mcp.mcp.server import DbtMCP

from dbt_mcp.tools.lightdash_list_spaces import (
    get_lightdash_list_spaces_tool,
    handle_lightdash_list_spaces,
)
from dbt_mcp.tools.lightdash_list_charts import (
    get_lightdash_list_charts_tool,
    handle_lightdash_list_charts,
)
from dbt_mcp.tools.lightdash_get_chart import (
    get_lightdash_get_chart_tool,
    handle_lightdash_get_chart,
)
from dbt_mcp.tools.lightdash_create_chart import (
    get_lightdash_create_chart_tool,
    handle_lightdash_create_chart,
)
# Removed: lightdash_save_query_as_chart (semantic layer tool)
# Use lightdash_run_metric_query or lightdash_create_chart instead
from dbt_mcp.tools.lightdash_list_explores import (
    get_lightdash_list_explores_tool,
    handle_lightdash_list_explores,
)
from dbt_mcp.tools.lightdash_get_explore import (
    get_lightdash_get_explore_tool,
    handle_lightdash_get_explore,
)
from dbt_mcp.tools.enhanced_list_metrics import (
    get_enhanced_list_metrics_tool,
    handle_enhanced_list_metrics,
)
from dbt_mcp.tools.lightdash_run_metric_query import (
    get_lightdash_run_metric_query_tool,
    handle_lightdash_run_metric_query,
)
from dbt_mcp.tools.lightdash_get_user import (
    get_lightdash_get_user_tool,
    handle_lightdash_get_user,
)
from dbt_mcp.tools.lightdash_get_embed_url import (
    get_lightdash_get_embed_url_tool,
    handle_lightdash_get_embed_url,
)

logger = logging.getLogger(__name__)


def register_lightdash_tools(
    mcp: Any,  # Using Any to avoid circular import
    lightdash_config: LightdashConfig,
    disable_tools: List[ToolName]
) -> None:
    """Register Lightdash tools with the MCP server"""
    
    config = mcp.config
    
    # List Spaces tool
    if ToolName.LIGHTDASH_LIST_SPACES not in disable_tools:
        tool_def = get_lightdash_list_spaces_tool()
        @mcp.tool(
            name=tool_def.name,
            description=tool_def.description,
            structured_output=False
        )
        async def list_spaces_handler(arguments):
            return await handle_lightdash_list_spaces(arguments, config)
        logger.info("Registered lightdash_list_spaces tool")
    
    # List Charts tool
    if ToolName.LIGHTDASH_LIST_CHARTS not in disable_tools:
        tool_def = get_lightdash_list_charts_tool()
        @mcp.tool(
            name=tool_def.name,
            description=tool_def.description,
            structured_output=False
        )
        async def lightdash_list_charts_handler(arguments):
            return await handle_lightdash_list_charts(arguments, config)
        logger.info("Registered lightdash_list_charts tool")
    
    # Get Chart tool
    if ToolName.LIGHTDASH_GET_CHART not in disable_tools:
        tool_def = get_lightdash_get_chart_tool()
        @mcp.tool(
            name=tool_def.name,
            description=tool_def.description,
            structured_output=False
        )
        async def lightdash_get_chart_handler(arguments):
            return await handle_lightdash_get_chart(arguments, config)
        logger.info("Registered lightdash_get_chart tool")
    
    # Create Chart tool
    if ToolName.LIGHTDASH_CREATE_CHART not in disable_tools:
        tool_def = get_lightdash_create_chart_tool()
        @mcp.tool(
            name=tool_def.name,
            description=tool_def.description,
            structured_output=False
        )
        async def lightdash_create_chart_handler(arguments):
            return await handle_lightdash_create_chart(arguments, config)
        logger.info("Registered lightdash_create_chart tool")
    
    # Note: lightdash_run_query (semantic layer tool) has been removed
    # Use lightdash_run_metric_query or lightdash_create_chart instead
    
    # List Explores tool
    if ToolName.LIGHTDASH_LIST_EXPLORES not in disable_tools:
        tool_def = get_lightdash_list_explores_tool()
        @mcp.tool(
            name=tool_def.name,
            description=tool_def.description,
            structured_output=False
        )
        async def lightdash_list_explores_handler(arguments):
            return await handle_lightdash_list_explores(arguments, config)
        logger.info("Registered lightdash_list_explores tool")
    
    # Get Explore tool
    if ToolName.LIGHTDASH_GET_EXPLORE not in disable_tools:
        tool_def = get_lightdash_get_explore_tool()
        @mcp.tool(
            name=tool_def.name,
            description=tool_def.description,
            structured_output=False
        )
        async def lightdash_get_explore_handler(arguments):
            return await handle_lightdash_get_explore(arguments, config)
        logger.info("Registered lightdash_get_explore tool")
    
    # Enhanced List Metrics tool
    # Note: This doesn't have a specific ToolName yet, so we check if Lightdash is enabled
    if config.lightdash_config:
        tool_def = get_enhanced_list_metrics_tool()
        @mcp.tool(
            name=tool_def.name,
            description=tool_def.description,
            structured_output=False
        )
        async def enhanced_list_metrics_handler(arguments):
            return await handle_enhanced_list_metrics(arguments, config)
        logger.info("Registered enhanced list_metrics_enhanced tool")
    
    # Run Metric Query tool (Lightdash-based semantic layer)
    if config.lightdash_config:
        tool_def = get_lightdash_run_metric_query_tool()
        @mcp.tool(
            name=tool_def.name,
            description=tool_def.description,
            structured_output=False
        )
        async def run_metric_query_handler(arguments):
            return await handle_lightdash_run_metric_query(arguments, config)
        logger.info("Registered lightdash_run_metric_query tool")
    
    # Get User tool
    if config.lightdash_config:
        tool_def = get_lightdash_get_user_tool()
        @mcp.tool(
            name=tool_def.name,
            description=tool_def.description,
            structured_output=False
        )
        async def get_user_handler(arguments):
            return await handle_lightdash_get_user(arguments, config)
        logger.info("Registered lightdash_get_user tool")
    
    # Get Embed URL tool
    if ToolName.LIGHTDASH_GET_EMBED_URL not in disable_tools:
        tool_def = get_lightdash_get_embed_url_tool()
        @mcp.tool(
            name=tool_def.name,
            description=tool_def.description,
            structured_output=False
        )
        async def get_embed_url_handler(arguments):
            return await handle_lightdash_get_embed_url(arguments, config)
        logger.info("Registered lightdash_get_embed_url tool")