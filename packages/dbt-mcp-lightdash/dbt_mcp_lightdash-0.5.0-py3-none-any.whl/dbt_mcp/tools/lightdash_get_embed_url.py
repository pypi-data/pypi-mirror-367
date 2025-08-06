"""Tool for generating Lightdash embed URLs"""

import json
import logging
from typing import Any, Dict, Optional, Literal, List

from mcp.types import Tool, TextContent

from dbt_mcp.config.config import Config
from dbt_mcp.lightdash.client import LightdashAPIClient
from dbt_mcp.tools.tool_names import ToolName
from dbt_mcp.prompts.prompts import get_prompt

logger = logging.getLogger(__name__)


def get_lightdash_get_embed_url_tool() -> Tool:
    """Get the Lightdash embed URL tool definition"""
    return Tool(
        name=ToolName.LIGHTDASH_GET_EMBED_URL.value,
        description="Generate an embed URL for a Lightdash chart or dashboard that can be displayed in an iframe",
        inputSchema={
            "type": "object",
            "properties": {
                "resource_uuid": {
                    "type": "string",
                    "description": "The UUID of the chart or dashboard to embed"
                },
                "resource_type": {
                    "type": "string",
                    "enum": ["chart", "dashboard"],
                    "description": "Whether this is a chart or dashboard",
                    "default": "chart"
                },
                "expires_in": {
                    "type": "string",
                    "description": "JWT expiration time (e.g., '1h', '8h', '24h', '7d')",
                    "default": "8h"
                },
                "dashboard_filters_interactivity": {
                    "type": "object",
                    "description": "Optional dashboard filter settings for interactivity"
                },
                "can_export_csv": {
                    "type": "boolean",
                    "description": "Allow CSV export from embedded view",
                    "default": False
                },
                "can_export_images": {
                    "type": "boolean",
                    "description": "Allow image export from embedded view",
                    "default": False
                },
                "return_markdown": {
                    "type": "boolean",
                    "description": "Return markdown directive for LibreChat rendering",
                    "default": True
                },
                "height": {
                    "type": "integer",
                    "description": "Height of the embed in pixels"
                }
            },
            "required": ["resource_uuid"]
        }
    )


async def handle_lightdash_get_embed_url(
    arguments: str,
    config: Config
) -> List[TextContent]:
    """Generate an embed URL for a Lightdash chart or dashboard."""
    try:
        # Parse arguments
        args = json.loads(arguments)
        resource_uuid = args["resource_uuid"]
        resource_type = args.get("resource_type", "chart")
        expires_in = args.get("expires_in", "8h")
        dashboard_filters_interactivity = args.get("dashboard_filters_interactivity")
        can_export_csv = args.get("can_export_csv", False)
        can_export_images = args.get("can_export_images", False)
        return_markdown = args.get("return_markdown", True)
        height = args.get("height")
        
        # Initialize Lightdash client
        lightdash_client = LightdashAPIClient(config.lightdash)
        project_uuid = config.lightdash.project_id
        
        # Prepare the request body
        embed_request = {
            "content": {
                "type": resource_type,
                "uuid": resource_uuid,
            },
            "expiresIn": expires_in,
        }
        
        # Add optional dashboard-specific settings
        if resource_type == "dashboard" and dashboard_filters_interactivity:
            embed_request["content"]["dashboardFiltersInteractivity"] = dashboard_filters_interactivity
        
        # Add export permissions
        if can_export_csv or can_export_images:
            embed_request["content"]["permissions"] = {
                "canExportCsv": can_export_csv,
                "canExportImages": can_export_images,
            }
        
        # Make the API request
        endpoint = f"/projects/{project_uuid}/embed/get-embed-url"
        response = await lightdash_client._make_request(
            method="POST",
            endpoint=endpoint,
            data=embed_request
        )
        
        if response["status"] != "ok":
            raise Exception(f"Failed to generate embed URL: {response}")
        
        embed_url = response["results"]["url"]
        
        # Get resource details for title
        if resource_type == "chart":
            chart_endpoint = f"/projects/{project_uuid}/saved/{resource_uuid}"
            chart_response = await lightdash_client._make_request("GET", chart_endpoint)
            title = chart_response["results"]["name"]
            default_height = 400
        else:
            dashboard_endpoint = f"/projects/{project_uuid}/dashboards/{resource_uuid}"
            dashboard_response = await lightdash_client._make_request("GET", dashboard_endpoint)
            title = dashboard_response["results"]["name"]
            default_height = 600
        
        # Determine height
        embed_height = height or default_height
        
        # Prepare response
        result = {
            "url": embed_url,
            "resource_type": resource_type,
            "resource_uuid": resource_uuid,
            "title": title,
            "expires_in": expires_in,
        }
        
        if return_markdown:
            # Generate markdown directive
            directive_type = f"lightdash-{resource_type}"
            markdown = f"""Here's the {title}:

:::{directive_type}{{url="{embed_url}" title="{title}" height="{embed_height}"}}
:::"""
            result["markdown"] = markdown
        
        # Format response
        if return_markdown and "markdown" in result:
            return [TextContent(type="text", text=result["markdown"])]
        else:
            # Return JSON response
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        logger.info(f"Generated embed URL for {resource_type} {resource_uuid}")
        
    except Exception as e:
        logger.error(f"Error generating embed URL: {str(e)}")
        error_msg = f"Failed to generate embed URL: {str(e)}"
        return [TextContent(type="text", text=error_msg)]