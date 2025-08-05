"""
FIS MCP Server - Python Implementation
Converted from Node.js MCP server for AWS Fault Injection Simulator
"""

import json
import asyncio
import logging
import os
from typing import Dict, Any, List, Optional, Union
import boto3
import requests

# MCP Python SDK imports
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FISService:
    """AWS FIS service wrapper for MCP operations"""
    
    def __init__(self):
        """Initialize FIS client with flexible credential handling"""
        try:
            # Try to load configuration from file first
            config = self._load_config()
            
            # Get AWS configuration from environment variables or config file
            region = os.getenv('AWS_REGION') or config.get('region', 'us-east-1')
            profile = os.getenv('AWS_PROFILE') or config.get('profile')
            
            # Initialize boto3 session
            if profile and profile != 'default':
                session = boto3.Session(profile_name=profile)
                self.client = session.client('fis', region_name=region)
                logger.info(f"Initialized FIS client with profile: {profile}, region: {region}")
            elif config.get('credentials', {}).get('access_key_id'):
                # Use credentials from config file
                creds = config['credentials']
                self.client = boto3.client(
                    'fis',
                    region_name=region,
                    aws_access_key_id=creds['access_key_id'],
                    aws_secret_access_key=creds['secret_access_key'],
                    aws_session_token=creds.get('session_token')
                )
                logger.info(f"Initialized FIS client with config file credentials, region: {region}")
            else:
                # Use default credentials (environment variables, IAM role, etc.)
                self.client = boto3.client('fis', region_name=region)
                logger.info(f"Initialized FIS client with default credentials, region: {region}")
                
        except Exception as e:
            logger.error(f"Failed to initialize FIS client: {str(e)}")
            raise Exception(f"AWS credentials not configured properly: {str(e)}")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from aws_config.json if it exists"""
        config_path = os.path.join(os.path.dirname(__file__), 'aws_config.json')
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load config file: {str(e)}")
        return {}
    
    async def create_experiment_template(self, params: Dict[str, Any]) -> types.CallToolResult:
        """Create a new AWS FIS experiment template"""
        try:
            input_params = {
                'description': params['description'],
                'roleArn': params['roleArn'],
                'actions': params['actions'],
                'targets': params.get('targets', {}),
                'stopConditions': params['stopConditions'],
            }
            
            # Add optional parameters
            if 'tags' in params:
                input_params['tags'] = params['tags']
            
            response = self.client.create_experiment_template(**input_params)
            
            result_text = f"Successfully created experiment template:\n{json.dumps(response['experimentTemplate'], indent=2, default=str)}"
            
            return types.CallToolResult(
                content=[types.TextContent(type="text", text=result_text)]
            )
            
        except Exception as error:
            raise Exception(f"Failed to create experiment template: {str(error)}")
    
    async def list_experiment_templates(self, params: Dict[str, Any] = None) -> types.CallToolResult:
        """List all AWS FIS experiment templates"""
        try:
            if params is None:
                params = {}
                
            input_params = {}
            if 'maxResults' in params:
                input_params['maxResults'] = params['maxResults']
            if 'nextToken' in params:
                input_params['nextToken'] = params['nextToken']
            
            response = self.client.list_experiment_templates(**input_params)
            templates = response.get('experimentTemplates', [])
            
            template_list = []
            for template in templates:
                template_list.append({
                    'id': template.get('id'),
                    'description': template.get('description'),
                    'creationTime': template.get('creationTime'),
                    'lastUpdateTime': template.get('lastUpdateTime'),
                    'tags': template.get('tags', {})
                })
            
            result_text = f"Found {len(templates)} experiment templates:\n{json.dumps(template_list, indent=2, default=str)}"
            
            return types.CallToolResult(
                content=[types.TextContent(type="text", text=result_text)]
            )
            
        except Exception as error:
            raise Exception(f"Failed to list experiment templates: {str(error)}")
    
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
    
    async def list_experiments(self, params: Dict[str, Any] = None) -> types.CallToolResult:
        """List all AWS FIS experiments"""
        try:
            if params is None:
                params = {}
                
            input_params = {}
            if 'maxResults' in params:
                input_params['maxResults'] = params['maxResults']
            if 'nextToken' in params:
                input_params['nextToken'] = params['nextToken']
            
            response = self.client.list_experiments(**input_params)
            experiments = response.get('experiments', [])
            
            experiment_list = []
            for experiment in experiments:
                experiment_list.append({
                    'id': experiment.get('id'),
                    'experimentTemplateId': experiment.get('experimentTemplateId'),
                    'state': experiment.get('state', {}),
                    'creationTime': experiment.get('creationTime'),
                    'tags': experiment.get('tags', {})
                })
            
            result_text = f"Found {len(experiments)} experiments:\n{json.dumps(experiment_list, indent=2, default=str)}"
            
            return types.CallToolResult(
                content=[types.TextContent(type="text", text=result_text)]
            )
            
        except Exception as error:
            raise Exception(f"Failed to list experiments: {str(error)}")
    
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
    
    async def get_aws_resources(self) -> types.CallToolResult:
        """Get AWS resources available for FIS experiments"""
        try:
            response = requests.get(
                'https://gqig3ff5qg.execute-api.ap-northeast-2.amazonaws.com/prod/search-services',
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            
            result_text = f"AWS Resources available for FIS experiments:\n{json.dumps(data, indent=2)}"
            
            return types.CallToolResult(
                content=[types.TextContent(type="text", text=result_text)]
            )
            
        except Exception as error:
            raise Exception(f"Failed to get AWS resources: {str(error)}")


class FISMCPServer:
    """FIS MCP Server implementation"""
    
    def __init__(self):
        """Initialize the MCP server"""
        self.server = mcp.server.Server("fis-mcp-server")
        self.fis_service = FISService()
        self.setup_tool_handlers()
    
    def setup_tool_handlers(self):
        """Setup tool handlers for the MCP server"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> types.ListToolsResult:
            """List available tools"""
            return types.ListToolsResult(
                tools=[
                    types.Tool(
                        name="create_experiment_template",
                        description="Create a new AWS FIS experiment template",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "description": {
                                    "type": "string",
                                    "description": "Description of the experiment template"
                                },
                                "roleArn": {
                                    "type": "string",
                                    "description": "IAM role ARN for the experiment"
                                },
                                "actions": {
                                    "type": "object",
                                    "description": "Actions to perform in the experiment"
                                },
                                "targets": {
                                    "type": "object",
                                    "description": "Targets for the experiment"
                                },
                                "stopConditions": {
                                    "type": "array",
                                    "description": "Stop conditions for the experiment"
                                },
                                "tags": {
                                    "type": "object",
                                    "description": "Tags for the experiment template"
                                }
                            },
                            "required": ["description", "roleArn", "actions", "stopConditions"]
                        }
                    ),
                    types.Tool(
                        name="list_experiment_templates",
                        description="List all AWS FIS experiment templates",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "maxResults": {
                                    "type": "number",
                                    "description": "Maximum number of results to return"
                                },
                                "nextToken": {
                                    "type": "string",
                                    "description": "Token for pagination"
                                }
                            }
                        }
                    ),
                    types.Tool(
                        name="get_experiment_template",
                        description="Get detailed information about a specific experiment template",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "id": {
                                    "type": "string",
                                    "description": "Experiment template ID"
                                }
                            },
                            "required": ["id"]
                        }
                    ),
                    types.Tool(
                        name="list_experiments",
                        description="List all AWS FIS experiments",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "maxResults": {
                                    "type": "number",
                                    "description": "Maximum number of results to return"
                                },
                                "nextToken": {
                                    "type": "string",
                                    "description": "Token for pagination"
                                }
                            }
                        }
                    ),
                    types.Tool(
                        name="get_experiment",
                        description="Get detailed information about a specific experiment",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "id": {
                                    "type": "string",
                                    "description": "Experiment ID"
                                }
                            },
                            "required": ["id"]
                        }
                    ),
                    types.Tool(
                        name="get_aws_resources",
                        description="Get AWS resources available for FIS experiments",
                        inputSchema={
                            "type": "object",
                            "properties": {}
                        }
                    )
                ]
            )
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> types.CallToolResult:
            """Handle tool calls"""
            try:
                if name == "create_experiment_template":
                    return await self.fis_service.create_experiment_template(arguments)
                
                elif name == "list_experiment_templates":
                    return await self.fis_service.list_experiment_templates(arguments)
                
                elif name == "get_experiment_template":
                    if not arguments or 'id' not in arguments:
                        raise ValueError("Missing required parameter: id")
                    return await self.fis_service.get_experiment_template(arguments['id'])
                
                elif name == "list_experiments":
                    return await self.fis_service.list_experiments(arguments)
                
                elif name == "get_experiment":
                    if not arguments or 'id' not in arguments:
                        raise ValueError("Missing required parameter: id")
                    return await self.fis_service.get_experiment(arguments['id'])
                
                elif name == "get_aws_resources":
                    return await self.fis_service.get_aws_resources()
                
                else:
                    raise ValueError(f"Unknown tool: {name}")
                    
            except Exception as error:
                logger.error(f"Error in tool call {name}: {str(error)}")
                return types.CallToolResult(
                    content=[types.TextContent(
                        type="text", 
                        text=f"Error: {str(error)}"
                    )]
                )
    
    async def run(self):
        """Run the MCP server"""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="fis-mcp-server",
                    server_version="1.1.0"
                )
            )


# Entry point for running the server
async def main():
    """Main entry point"""
    server = FISMCPServer()
    logger.info("FIS MCP server starting...")
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
