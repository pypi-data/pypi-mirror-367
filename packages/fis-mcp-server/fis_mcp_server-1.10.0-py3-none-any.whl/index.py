"""
FIS MCP Server - Python Implementation
Converted from Node.js MCP server for AWS Fault Injection Simulator
"""

import json
import asyncio
import logging
import os
from typing import Dict, Any, List
import boto3
import requests

# MCP Python SDK imports
from mcp.server.models import InitializationOptions
import mcp.server.stdio
from mcp.server.fastmcp import FastMCP
import mcp.types as types


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("fis-mcp-server")


def _load_config(self) -> Dict[str, Any]:
    """Load configuration from aws_config.json if it exists"""
    config_path = os.path.join(os.path.dirname(__file__), "aws_config.json")
    try:
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                return json.load(f)
    except Exception as e:
        logger.warning(f"Could not load config file: {str(e)}")
    return {}


@mcp.tool()
async def create_experiment_template(
    self, params: Dict[str, Any]
) -> types.CallToolResult:
    """Create a new AWS FIS experiment template"""
    try:
        # Validate and clean actions to remove unsupported parameters
        cleaned_actions = self._clean_actions(params["actions"])

        input_params = {
            "description": params["description"],
            "roleArn": params["roleArn"],
            "actions": cleaned_actions,
            "targets": params.get("targets", {}),
            "stopConditions": params["stopConditions"],
        }

        # Add optional parameters
        if "tags" in params:
            input_params["tags"] = params["tags"]

        response = self.client.create_experiment_template(**input_params)

        result_text = f"Successfully created experiment template:\n{json.dumps(response['experimentTemplate'], indent=2, default=str)}"

        return types.CallToolResult(
            content=[types.TextContent(type="text", text=result_text)]
        )

    except Exception as error:
        raise Exception(f"Failed to create experiment template: {str(error)}")


@mcp.tool()
def _clean_actions(self, actions: Dict[str, Any]) -> Dict[str, Any]:
    """Clean actions to remove unsupported parameters based on action type"""
    cleaned_actions = {}

    # Actions that don't support duration parameter
    no_duration_actions = [
        "aws:ec2:reboot-instances",
        "aws:ec2:stop-instances",
        "aws:ec2:terminate-instances",
        "aws:rds:failover-db-cluster",
        "aws:rds:reboot-db-instances",
    ]

    for action_name, action_config in actions.items():
        cleaned_config = action_config.copy()

        # Remove duration parameter for actions that don't support it
        if action_config.get("actionId") in no_duration_actions:
            if (
                "parameters" in cleaned_config
                and "duration" in cleaned_config["parameters"]
            ):
                logger.warning(
                    f"Removing unsupported 'duration' parameter from action {action_config.get('actionId')}"
                )
                del cleaned_config["parameters"]["duration"]
                # If parameters is now empty, remove it entirely
                if not cleaned_config["parameters"]:
                    del cleaned_config["parameters"]

        cleaned_actions[action_name] = cleaned_config

    return cleaned_actions


@mcp.tool()
async def list_experiment_templates(
    self, params: Dict[str, Any] = None
) -> types.CallToolResult:
    """List all AWS FIS experiment templates"""
    try:
        if params is None:
            params = {}

        input_params = {}
        if "maxResults" in params:
            input_params["maxResults"] = params["maxResults"]
        if "nextToken" in params:
            input_params["nextToken"] = params["nextToken"]

        response = self.client.list_experiment_templates(**input_params)
        templates = response.get("experimentTemplates", [])

        template_list = []
        for template in templates:
            template_list.append(
                {
                    "id": template.get("id"),
                    "description": template.get("description"),
                    "creationTime": template.get("creationTime"),
                    "lastUpdateTime": template.get("lastUpdateTime"),
                    "tags": template.get("tags", {}),
                }
            )

        result_text = f"Found {len(templates)} experiment templates:\n{json.dumps(template_list, indent=2, default=str)}"

        return types.CallToolResult(
            content=[types.TextContent(type="text", text=result_text)]
        )

    except Exception as error:
        raise Exception(f"Failed to list experiment templates: {str(error)}")


@mcp.tool()
async def get_experiment_template(self, template_id: str) -> types.CallToolResult:
    """Get detailed information about a specific experiment template"""
    try:
        response = self.client.get_experiment_template(id=template_id)

        result_text = f"Experiment template details:\n{json.dumps(response['experimentTemplate'], indent=2, default=str)}"

        return types.CallToolResult(
            content=[types.TextContent(type="text", text=result_text)]
        )

    except Exception as error:
        raise Exception(f"Failed to get experiment template: {str(error)}")


@mcp.tool()
async def list_experiments(self, params: Dict[str, Any] = None) -> types.CallToolResult:
    """List all AWS FIS experiments"""
    try:
        if params is None:
            params = {}

        input_params = {}
        if "maxResults" in params:
            input_params["maxResults"] = params["maxResults"]
        if "nextToken" in params:
            input_params["nextToken"] = params["nextToken"]

        response = self.client.list_experiments(**input_params)
        experiments = response.get("experiments", [])

        experiment_list = []
        for experiment in experiments:
            experiment_list.append(
                {
                    "id": experiment.get("id"),
                    "experimentTemplateId": experiment.get("experimentTemplateId"),
                    "state": experiment.get("state", {}),
                    "creationTime": experiment.get("creationTime"),
                    "tags": experiment.get("tags", {}),
                }
            )

        result_text = f"Found {len(experiments)} experiments:\n{json.dumps(experiment_list, indent=2, default=str)}"

        return types.CallToolResult(
            content=[types.TextContent(type="text", text=result_text)]
        )

    except Exception as error:
        raise Exception(f"Failed to list experiments: {str(error)}")


@mcp.tool()
async def get_experiment(self, experiment_id: str) -> types.CallToolResult:
    """Get detailed information about a specific experiment"""
    try:
        response = self.client.get_experiment(id=experiment_id)

        result_text = f"Experiment details:\n{json.dumps(response['experiment'], indent=2, default=str)}"

        return types.CallToolResult(
            content=[types.TextContent(type="text", text=result_text)]
        )

    except Exception as error:
        raise Exception(f"Failed to get experiment: {str(error)}")


@mcp.tool()
async def get_aws_resources(self) -> types.CallToolResult:
    """Get AWS resources available for FIS experiments"""
    try:
        response = requests.get(
            "https://gqig3ff5qg.execute-api.ap-northeast-2.amazonaws.com/prod/search-services",
            timeout=30,
        )
        response.raise_for_status()

        data = response.json()

        result_text = f"AWS Resources available for FIS experiments:\n{json.dumps(data, indent=2)}"

        return types.CallToolResult(
            content=[types.TextContent(type="text", text=result_text)]
        )

    except Exception as error:
        raise Exception(f"Failed to get AWS resources: {str(error)}")


@mcp.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List available tools"""
    logger.info("Handling list_tools request")

    tools = [
        types.Tool(
            name="create_experiment_template",
            description="Create a new AWS FIS experiment template",
            inputSchema={
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Description of the experiment template",
                    },
                    "roleArn": {
                        "type": "string",
                        "description": "IAM role ARN for the experiment",
                    },
                    "actions": {
                        "type": "object",
                        "description": "Actions to perform in the experiment",
                    },
                    "targets": {
                        "type": "object",
                        "description": "Targets for the experiment",
                    },
                    "stopConditions": {
                        "type": "array",
                        "description": "Stop conditions for the experiment",
                    },
                    "tags": {
                        "type": "object",
                        "description": "Tags for the experiment template",
                    },
                },
                "required": [
                    "description",
                    "roleArn",
                    "actions",
                    "stopConditions",
                ],
            },
        ),
        types.Tool(
            name="list_experiment_templates",
            description="List all AWS FIS experiment templates",
            inputSchema={
                "type": "object",
                "properties": {
                    "maxResults": {
                        "type": "number",
                        "description": "Maximum number of results to return",
                    },
                    "nextToken": {
                        "type": "string",
                        "description": "Token for pagination",
                    },
                },
            },
        ),
        types.Tool(
            name="get_experiment_template",
            description="Get detailed information about a specific experiment template",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "Experiment template ID",
                    }
                },
                "required": ["id"],
            },
        ),
        types.Tool(
            name="list_experiments",
            description="List all AWS FIS experiments",
            inputSchema={
                "type": "object",
                "properties": {
                    "maxResults": {
                        "type": "number",
                        "description": "Maximum number of results to return",
                    },
                    "nextToken": {
                        "type": "string",
                        "description": "Token for pagination",
                    },
                },
            },
        ),
        types.Tool(
            name="get_experiment",
            description="Get detailed information about a specific experiment",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {"type": "string", "description": "Experiment ID"}
                },
                "required": ["id"],
            },
        ),
        types.Tool(
            name="get_aws_resources",
            description="Get AWS resources available for FIS experiments including EC2, ECS, RDS, and Lambda",
            inputSchema={
                "type": "object",
                "properties": {
                    "resource_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific resource types to query (ec2, ecs, rds, lambda). If not specified, all types are queried.",
                    },
                    "include_fis_targets": {
                        "type": "boolean",
                        "description": "Whether to include FIS-compatible target definitions",
                        "default": True,
                    },
                },
            },
        ),
    ]

    # 각 도구가 올바른 형식인지 확인
    for i, tool in enumerate(tools):
        logger.info(f"Tool {i}: {type(tool)} - {getattr(tool, 'name', 'NO_NAME')}")
        if not hasattr(tool, "name"):
            logger.error(f"Tool missing name attribute: {tool}")
            raise ValueError(f"Invalid tool definition: {tool}")

    logger.info(f"Returning {len(tools)} tools")
    return tools


@mcp.call_tool()
async def handle_call_tool(
    name: str, arguments: Dict[str, Any]
) -> types.CallToolResult:
    """Handle tool calls"""
    try:
        if name == "create_experiment_template":
            return await create_experiment_template(arguments)

        elif name == "list_experiment_templates":
            return await list_experiment_templates(arguments)

        elif name == "get_experiment_template":
            if not arguments or "id" not in arguments:
                raise ValueError("Missing required parameter: id")
            return await get_experiment_template(arguments["id"])

        elif name == "list_experiments":
            return await list_experiments(arguments)

        elif name == "get_experiment":
            if not arguments or "id" not in arguments:
                raise ValueError("Missing required parameter: id")
            return await get_experiment(arguments["id"])

        elif name == "get_aws_resources":
            return await get_aws_resources()

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as error:
        logger.error(f"Error in tool call {name}: {str(error)}")
        return types.CallToolResult(
            content=[types.TextContent(type="text", text=f"Error: {str(error)}")]
        )


if __name__ == "__main__":
    mcp.run(transport="stdio")
