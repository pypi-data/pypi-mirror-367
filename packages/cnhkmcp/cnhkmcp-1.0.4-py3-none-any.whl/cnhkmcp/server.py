"""
MCP server implementation for quantitative research platform.
"""

import asyncio
import logging
import sys
from typing import Any, Dict, List, Optional, Sequence

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool
from pydantic import BaseModel, Field

from .client import ApiClient
from .config import config_manager
from .utils import (
    combine_pnl_data,
    combine_test_results,
    expand_nested_data,
    generate_alpha_links,
    prettify_results,
    save_pnl_data,
    save_simulation_data,
    save_yearly_statistics,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)


# Pydantic models for request validation
class AuthenticateRequest(BaseModel):
    email: str = Field(description="Email address for platform account")
    password: str = Field(description="Password for platform account")


class SimulationSettings(BaseModel):
    instrumentType: str = Field(description="Instrument type (e.g., EQUITY)")
    region: str = Field(description="Region (e.g., USA)")
    universe: str = Field(description="Universe (e.g., TOP3000)")
    delay: int = Field(ge=0, le=1, description="Delay (0 or 1)")
    decay: float = Field(description="Decay value")
    neutralization: str = Field(description="Neutralization method")
    truncation: float = Field(description="Truncation value")
    testPeriod: str = Field(description="Test period (e.g., P1Y6M)")
    unitHandling: str = Field(description="Unit handling method")
    nanHandling: str = Field(description="NaN handling method")
    language: str = Field(description="Language (e.g., FASTEXPR)")
    visualization: bool = Field(description="Enable visualization")
    maxTrade: Optional[str] = Field(None, description="Max trade setting")
    pasteurization: Optional[str] = Field(None, description="Pasteurization setting")


class CreateSimulationRequest(BaseModel):
    type: str = Field(description="Type of simulation (REGULAR or SUPER)")
    settings: SimulationSettings
    regular: Optional[str] = Field(None, description="Regular simulation code")
    combo: Optional[str] = Field(None, description="Combo code for SUPER simulation")
    selection: Optional[str] = Field(None, description="Selection code for SUPER simulation")


class MultiSimulationRequest(BaseModel):
    simulations: List[CreateSimulationRequest] = Field(max_length=10, description="List of simulations (max 10)")


class CNHKMCPServer:
    """MCP Server for quantitative research platform."""

    def __init__(self):
        self.client = ApiClient()
        self.server = Server("cnhkmcp")
        self._setup_tools()

    def _setup_tools(self) -> None:
        """Set up all MCP tools."""
        
        # Authentication
        @self.server.call_tool()
        async def authenticate(arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
            """Authenticate with platform."""
            req = AuthenticateRequest(**arguments)
            
            try:
                result = await self.client.authenticate(req.email, req.password)
                
                # Store credentials for future use
                config_manager.set_credentials(req.email, req.password)
                
                return [{
                    "type": "text",
                    "text": f"Successfully authenticated with platform. User ID: {result.get('user', {}).get('id', 'unknown')}"
                }]
            except Exception as e:
                logger.error(f"Authentication failed: {e}")
                return [{
                    "type": "text", 
                    "text": f"Authentication failed: {str(e)}"
                }]

        # Simulation Management
        @self.server.call_tool()
        async def create_simulation(arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
            """Submit expressions for simulation."""
            req = CreateSimulationRequest(**arguments)
            
            try:
                result = await self.client.create_simulation(req.dict())
                
                return [{
                    "type": "text",
                    "text": f"Simulation created successfully. ID: {result.get('id', 'unknown')}"
                }, {
                    "type": "text",
                    "text": f"Simulation details: {result}"
                }]
            except Exception as e:
                logger.error(f"Simulation creation failed: {e}")
                return [{
                    "type": "text",
                    "text": f"Simulation creation failed: {str(e)}"
                }]

        @self.server.call_tool()
        async def create_multi_simulation(arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
            """Submit multiple expressions for batch simulation."""
            req = MultiSimulationRequest(**arguments)
            
            try:
                result = await self.client.create_multi_simulation([s.dict() for s in req.simulations])
                
                return [{
                    "type": "text",
                    "text": f"Multi-simulation created with {len(req.simulations)} models. Batch ID: {result.get('batch_id', 'unknown')}"
                }, {
                    "type": "text",
                    "text": f"Simulation details: {result}"
                }]
            except Exception as e:
                logger.error(f"Multi-simulation creation failed: {e}")
                return [{
                    "type": "text",
                    "text": f"Multi-simulation creation failed: {str(e)}"
                }]

        @self.server.call_tool()
        async def get_simulation_status(arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
            """Check simulation progress and retrieve completion status."""
            simulation_id = arguments.get("simulationId")
            if not simulation_id:
                return [{"type": "text", "text": "simulationId is required"}]
            
            try:
                result = await self.client.get_simulation_status(simulation_id)
                
                return [{
                    "type": "text",
                    "text": f"Simulation {simulation_id} status: {result.get('status', 'unknown')}"
                }, {
                    "type": "text",
                    "text": f"Details: {result}"
                }]
            except Exception as e:
                logger.error(f"Failed to get simulation status: {e}")
                return [{
                    "type": "text",
                    "text": f"Failed to get simulation status: {str(e)}"
                }]

        @self.server.call_tool()
        async def wait_for_simulation(arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
            """Intelligent simulation waiting with automatic retry logic."""
            simulation_id = arguments.get("simulationId")
            max_wait_time = arguments.get("maxWaitTime", 1800)
            retry_interval = arguments.get("retryInterval", 10)
            
            if not simulation_id:
                return [{"type": "text", "text": "simulationId is required"}]
            
            try:
                result = await self.client.wait_for_simulation(
                    simulation_id, max_wait_time, retry_interval
                )
                
                return [{
                    "type": "text",
                    "text": f"Simulation {simulation_id} completed with status: {result.get('status')}"
                }, {
                    "type": "text",
                    "text": f"Final results: {result}"
                }]
            except Exception as e:
                logger.error(f"Simulation waiting failed: {e}")
                return [{
                    "type": "text",
                    "text": f"Simulation waiting failed: {str(e)}"
                }]

        # Alpha Management
        @self.server.call_tool()
        async def get_alpha_details(arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
            """Get comprehensive model metadata and simulation results."""
            alpha_id = arguments.get("alphaId")
            if not alpha_id:
                return [{"type": "text", "text": "alphaId is required"}]
            
            try:
                result = await self.client.get_alpha_details(alpha_id)
                
                return [{
                    "type": "text",
                    "text": f"Model {alpha_id} details retrieved successfully"
                }, {
                    "type": "text",
                    "text": f"Details: {result}"
                }]
            except Exception as e:
                logger.error(f"Failed to get model details: {e}")
                return [{
                    "type": "text",
                    "text": f"Failed to get model details: {str(e)}"
                }]

        @self.server.call_tool()
        async def get_user_alphas(arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
            """Retrieve user's IS/OS model list with pagination."""
            stage = arguments.get("stage")
            limit = arguments.get("limit", 100)
            offset = arguments.get("offset", 0)
            
            if not stage:
                return [{"type": "text", "text": "stage is required (IS or OS)"}]
            
            try:
                result = await self.client.get_user_alphas(stage, limit, offset)
                
                return [{
                    "type": "text",
                    "text": f"Retrieved {len(result.get('results', []))} {stage} models"
                }, {
                    "type": "text",
                    "text": f"Model list: {result}"
                }]
            except Exception as e:
                logger.error(f"Failed to get user models: {e}")
                return [{
                    "type": "text",
                    "text": f"Failed to get user models: {str(e)}"
                }]

        # Data Analysis Tools
        @self.server.call_tool()
        async def combine_pnl_data(arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
            """Aggregate PnL data from multiple models for portfolio analysis."""
            results = arguments.get("results", [])
            
            try:
                combined = combine_pnl_data(results)
                
                return [{
                    "type": "text",
                    "text": f"Combined PnL data from {combined['summary']['total_alphas']} models"
                }, {
                    "type": "text",
                    "text": f"Combined data: {combined}"
                }]
            except Exception as e:
                logger.error(f"Failed to combine PnL data: {e}")
                return [{
                    "type": "text",
                    "text": f"Failed to combine PnL data: {str(e)}"
                }]

        @self.server.call_tool()
        async def save_simulation_data(arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
            """Save complete simulation results to local JSON files."""
            simulation_result = arguments.get("simulationResult")
            folder_path = arguments.get("folderPath", "simulation_results")
            
            if not simulation_result:
                return [{"type": "text", "text": "simulationResult is required"}]
            
            try:
                result = save_simulation_data(simulation_result, folder_path)
                
                return [{
                    "type": "text",
                    "text": f"Simulation data saved to {result['filepath']}"
                }]
            except Exception as e:
                logger.error(f"Failed to save simulation data: {e}")
                return [{
                    "type": "text",
                    "text": f"Failed to save simulation data: {str(e)}"
                }]

        # Forum Tools
        @self.server.call_tool()
        async def get_forum_post(arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
            """Complete forum post reader with flexible input support."""
            post_url_or_id = arguments.get("postUrlOrId")
            email = arguments.get("email")
            password = arguments.get("password")
            include_comments = arguments.get("includeComments", True)
            headless = arguments.get("headless", True)
            
            # Try to get credentials from config if not provided
            if not email or not password:
                creds = config_manager.get_credentials()
                if creds:
                    email = email or creds["email"]
                    password = password or creds["password"]
            
            if not post_url_or_id or not email or not password:
                return [{"type": "text", "text": "postUrlOrId, email, and password are required"}]
            
            try:
                result = await self.client.get_forum_post(
                    post_url_or_id, email, password, include_comments, headless
                )
                
                return [{
                    "type": "text",
                    "text": f"Forum post retrieved: {result['title']}"
                }, {
                    "type": "text",
                    "text": f"Content: {result}"
                }]
            except Exception as e:
                logger.error(f"Failed to get forum post: {e}")
                return [{
                    "type": "text",
                    "text": f"Failed to get forum post: {str(e)}"
                }]

        # Register all tools with list_tools handler
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List available tools."""
            return [
                Tool(
                    name="authenticate",
                    description="🔐 REQUIRED FIRST: Authenticate with platform to start any research workflow",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "email": {"type": "string", "description": "Email address for platform account"},
                            "password": {"type": "string", "description": "Password for platform account"}
                        },
                        "required": ["email", "password"]
                    }
                ),
                Tool(
                    name="create_simulation",
                    description="🚀 CORE RESEARCH: Submit expressions for simulation",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "type": {"type": "string", "enum": ["REGULAR", "SUPER"]},
                            "settings": {
                                "type": "object",
                                "properties": {
                                    "instrumentType": {"type": "string"},
                                    "region": {"type": "string"},
                                    "universe": {"type": "string"},
                                    "delay": {"type": "integer", "minimum": 0, "maximum": 1},
                                    "decay": {"type": "number"},
                                    "neutralization": {"type": "string"},
                                    "truncation": {"type": "number"},
                                    "testPeriod": {"type": "string"},
                                    "unitHandling": {"type": "string"},
                                    "nanHandling": {"type": "string"},
                                    "language": {"type": "string"},
                                    "visualization": {"type": "boolean"}
                                },
                                "required": ["instrumentType", "region", "universe", "delay", "decay", 
                                           "neutralization", "truncation", "testPeriod", "unitHandling", 
                                           "nanHandling", "language", "visualization"]
                            },
                            "regular": {"type": "string"},
                            "combo": {"type": "string"},
                            "selection": {"type": "string"}
                        },
                        "required": ["type", "settings"]
                    }
                ),
                Tool(
                    name="create_multi_simulation",
                    description="🚀 BATCH RESEARCH: Submit multiple expressions for simultaneous simulation",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "simulations": {
                                "type": "array",
                                "maxItems": 10,
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "type": {"type": "string", "enum": ["REGULAR", "SUPER"]},
                                        "settings": {"type": "object"},
                                        "regular": {"type": "string"},
                                        "combo": {"type": "string"},
                                        "selection": {"type": "string"}
                                    },
                                    "required": ["type", "settings"]
                                }
                            }
                        },
                        "required": ["simulations"]
                    }
                ),
                Tool(
                    name="get_simulation_status",
                    description="⏱️ MONITORING: Check simulation progress and retrieve completion status",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "simulationId": {"type": "string"}
                        },
                        "required": ["simulationId"]
                    }
                ),
                Tool(
                    name="wait_for_simulation",
                    description="⏳ SMART MONITORING: Intelligent simulation waiting with automatic retry logic",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "simulationId": {"type": "string"},
                            "maxWaitTime": {"type": "integer", "default": 1800},
                            "retryInterval": {"type": "integer", "default": 10}
                        },
                        "required": ["simulationId"]
                    }
                ),
                Tool(
                    name="get_alpha_details",
                    description="📊 RESULT EXTRACTION: Get model metadata and simulation results",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "alphaId": {"type": "string"}
                        },
                        "required": ["alphaId"]
                    }
                ),
                Tool(
                    name="get_user_alphas",
                    description="📋 MODEL MANAGEMENT: Retrieve user's IS/OS model list with pagination",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "stage": {"type": "string", "enum": ["IS", "OS"]},
                            "limit": {"type": "integer", "default": 100},
                            "offset": {"type": "integer", "default": 0}
                        },
                        "required": ["stage"]
                    }
                ),
                Tool(
                    name="combine_pnl_data",
                    description="📈 PORTFOLIO ANALYSIS: Aggregate PnL data from multiple models",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "results": {"type": "array", "items": {"type": "object"}}
                        },
                        "required": ["results"]
                    }
                ),
                Tool(
                    name="save_simulation_data",
                    description="💾 RESEARCH ARCHIVAL: Save complete simulation results to local JSON files",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "simulationResult": {"type": "object"},
                            "folderPath": {"type": "string", "default": "simulation_results"}
                        },
                        "required": ["simulationResult"]
                    }
                ),
                Tool(
                    name="get_forum_post",
                    description="📄 COMPLETE FORUM POST READER: Extract comprehensive forum post content",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "postUrlOrId": {"type": "string"},
                            "email": {"type": "string"},
                            "password": {"type": "string"},
                            "includeComments": {"type": "boolean", "default": True},
                            "headless": {"type": "boolean", "default": True}
                        },
                        "required": ["postUrlOrId"]
                    }
                )
            ]

    async def run(self) -> None:
        """Run the MCP server."""
        try:
            logger.info("Starting CNHKMCP Server")
            
            # Initialize with stored credentials if available
            creds = config_manager.get_credentials()
            if creds:
                logger.info("Found stored credentials, attempting authentication")
                try:
                    await self.client.authenticate(creds["email"], creds["password"])
                    logger.info("Auto-authentication successful")
                except Exception as e:
                    logger.warning(f"Auto-authentication failed: {e}")
            
            # Start the server
            logger.info("Starting MCP server with stdio transport")
            async with stdio_server() as streams:
                await self.server.run(streams[0], streams[1])
                
        except Exception as e:
            logger.error(f"Server error: {e}", exc_info=True)
            raise
        finally:
            try:
                await self.client.close()
            except Exception as e:
                logger.warning(f"Error closing client: {e}")

    async def close(self) -> None:
        """Close the server and cleanup resources."""
        await self.client.close()


async def main() -> None:
    """Main entry point."""
    try:
        server = CNHKMCPServer()
        await server.run()
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)


def cli_main() -> None:
    """CLI entry point that handles async main."""
    asyncio.run(main())


if __name__ == "__main__":
    cli_main()
