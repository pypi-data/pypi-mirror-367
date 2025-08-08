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
    # Check if Lightdash is configured
    if not config.lightdash_config:
        return [
            TextContent(
                type="text",
                text="Error: Lightdash configuration not found. Please check your environment variables."
            )
        ]
    
    try:
        # Parse arguments - handle both string and dict inputs
        if isinstance(arguments, str):
            args = json.loads(arguments)
        else:
            args = arguments
        resource_uuid = args["resource_uuid"]
        resource_type = args.get("resource_type", "chart")
        expires_in = args.get("expires_in", "8h")
        dashboard_filters_interactivity = args.get("dashboard_filters_interactivity")
        can_export_csv = args.get("can_export_csv", False)
        can_export_images = args.get("can_export_images", False)
        return_markdown = args.get("return_markdown", True)
        height = args.get("height")
        
        # Initialize Lightdash client
        lightdash_client = LightdashAPIClient(config.lightdash_config)
        project_uuid = config.lightdash_config.project_id
        
        # Check if resource type is supported
        if resource_type != "dashboard":
            return [
                TextContent(
                    type="text",
                    text="Error: Only dashboards can be embedded. Individual charts must be added to a dashboard first."
                )
            ]
        
        # Try to get organizationUuid
        organization_uuid = None
        try:
            # Try to get user info for organizationUuid
            user_info = await lightdash_client.get_user()
            organization_uuid = user_info.get("organizationUuid")
        except Exception as e:
            # If user endpoint fails (e.g., PAT permissions), try to get from project
            logger.warning(f"Failed to get user info: {str(e)}. Trying project info.")
            try:
                project_endpoint = f"/projects/{project_uuid}"
                project_response = await lightdash_client._make_request("GET", project_endpoint)
                organization_uuid = project_response.get("results", {}).get("organizationUuid")
            except Exception as e2:
                logger.warning(f"Failed to get organization UUID from project: {str(e2)}")
        
        # Prepare the request body
        embed_request = {
            "content": {
                "type": "dashboard",
                "dashboardUuid": resource_uuid,
            },
            "expiresIn": expires_in,
        }
        
        # Add organizationUuid to userAttributes for row-level security
        if organization_uuid:
            embed_request["userAttributes"] = {
                "organizationUuid": organization_uuid
            }
        
        # Add optional dashboard-specific settings
        if dashboard_filters_interactivity:
            embed_request["content"]["dashboardFiltersInteractivity"] = dashboard_filters_interactivity
        
        # Add export permissions
        if can_export_csv or can_export_images:
            embed_request["content"]["permissions"] = {
                "canExportCsv": can_export_csv,
                "canExportImages": can_export_images,
            }
        
        # Make the API request
        endpoint = f"/embed/{project_uuid}/get-embed-url"
        response = await lightdash_client._make_request(
            method="POST",
            endpoint=endpoint,
            data=embed_request
        )
        
        if response["status"] != "ok":
            raise Exception(f"Failed to generate embed URL: {response}")
        
        embed_url = response["results"]["url"]
        
        # Get dashboard details for title
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
            markdown = f"""Here's the {title} dashboard:

:::lightdash-dashboard{{url="{embed_url}" title="{title}" height="{embed_height}"}}
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
        error_msg = str(e)
        
        # Provide helpful error messages
        if "embedService" in error_msg and "no factory or provider" in error_msg:
            error_msg = ("Embedding is not available in your Lightdash instance. "
                        "This feature requires an enterprise license or needs to be "
                        "enabled in your Bratrax fork.")
        elif "422" in error_msg:
            error_msg = f"Invalid request to embed API: {error_msg}"
        elif "404" in error_msg:
            error_msg = "Dashboard not found. Please check the dashboard UUID."
        else:
            error_msg = f"Failed to generate embed URL: {error_msg}"
            
        return [TextContent(type="text", text=error_msg)]