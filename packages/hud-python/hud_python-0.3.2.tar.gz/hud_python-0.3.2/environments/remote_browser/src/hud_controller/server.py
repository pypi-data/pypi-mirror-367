"""MCP server for remote browser environment."""

import asyncio
import sys
import logging
import os
from typing import Literal, Optional, Any
from pathlib import Path

# Configure logging
logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format="[%(levelname)s] %(asctime)s | %(name)s | %(message)s",
    force=True,
)
logger = logging.getLogger(__name__)

from mcp.server.fastmcp import FastMCP, Context
from pydantic import Field
from mcp.types import InitializeRequest, InitializeResult, Implementation
from mcp.shared.context import RequestContext
from mcp.server.models import InitializationOptions

# Import tools from SDK
from hud.tools.helper import mcp_intialize_wrapper, register_instance_tool
from .playwright_with_memory import PlaywrightToolWithMemory
from .browser_computer_tool import BrowserComputerTool

# Import providers and runtime
from .providers import get_provider, BrowserProvider
from .runtime import setup_tool, evaluate_tool

# Import registries for resources
from .evaluators import EvaluatorRegistry
from .setup import SetupRegistry
from .problems import ProblemRegistry

# Global state
browser_provider: Optional[BrowserProvider] = None
playwright_tool: Optional[PlaywrightToolWithMemory] = None
browser_computer: Optional[BrowserComputerTool] = None


@mcp_intialize_wrapper()
async def initialize_environment(session=None, progress_token=None):
    """Initialize the remote browser environment with progress reporting."""
    global browser_provider, playwright_tool, browser_computer

    async def send_progress(progress: int, message: str):
        if progress_token and session:
            await session.send_progress_notification(
                progress_token=progress_token,
                progress=progress,
                total=100,
                message=message,
            )
        logger.info(f"[{progress}%] {message}")

    try:
        await send_progress(10, "Starting remote browser environment initialization...")

        # Get provider configuration from environment
        provider_name = os.getenv("BROWSER_PROVIDER")
        if not provider_name:
            error_msg = (
                "BROWSER_PROVIDER environment variable is required. "
                "Supported providers: anchorbrowser, steel, browserbase, hyperbrowser, kernel"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)

        provider_name = provider_name.lower()
        await send_progress(20, f"Using browser provider: {provider_name}")

        # Initialize the browser provider
        provider_class = get_provider(provider_name)
        provider_config = {}

        # Add provider-specific configuration
        if provider_name == "anchorbrowser":
            provider_config["api_key"] = os.getenv("ANCHOR_API_KEY")
            provider_config["base_url"] = os.getenv(
                "ANCHOR_BASE_URL", "https://api.anchorbrowser.io"
            )

        browser_provider = provider_class(provider_config)
        await send_progress(30, "Browser provider initialized")

        # Launch the browser and get CDP URL
        await send_progress(40, "Launching remote browser...")

        # Build launch options
        launch_options = {}

        # Add proxy configuration if environment variables are set
        proxy_type = os.getenv("BROWSER_PROXY_TYPE")
        if proxy_type:
            if proxy_type == "custom":
                proxy_config = {
                    "type": "custom",
                    "server": os.getenv("BROWSER_PROXY_SERVER"),
                    "username": os.getenv("BROWSER_PROXY_USERNAME"),
                    "password": os.getenv("BROWSER_PROXY_PASSWORD"),
                    "active": True,
                }
            elif proxy_type == "anchor_residential":
                proxy_config = {
                    "type": "anchor_residential",
                    "country_code": os.getenv("BROWSER_PROXY_COUNTRY", "us"),
                    "active": True,
                }
            else:
                proxy_config = None

            if proxy_config:
                launch_options["proxy"] = proxy_config
                await send_progress(45, f"Using {proxy_type} proxy")

        # Add other launch options from environment
        max_duration = os.getenv("BROWSER_MAX_DURATION")
        if max_duration:
            launch_options["max_duration"] = int(max_duration)
        idle_timeout = os.getenv("BROWSER_IDLE_TIMEOUT")
        if idle_timeout:
            launch_options["idle_timeout"] = int(idle_timeout)

        # Create browser session
        cdp_url = await browser_provider.launch(**launch_options)

        # The provider already returns the proper CDP URL
        session_id = browser_provider._instance_id

        await send_progress(60, f"Remote browser launched, session ID: {session_id}")

        # Initialize playwright tool with memory and CDP URL
        await send_progress(70, "Initializing Playwright tool with memory...")
        playwright_tool = PlaywrightToolWithMemory(cdp_url=cdp_url)

        # Register tools with MCP
        register_instance_tool(mcp, "playwright", playwright_tool)
        await send_progress(80, "Playwright tool registered")

        # Register browser computer tool
        browser_computer = BrowserComputerTool(playwright_tool)
        register_instance_tool(mcp, "computer", browser_computer)
        await send_progress(85, "Browser computer tool registered")

        # Ensure browser is connected
        await playwright_tool._ensure_browser()
        await send_progress(90, "Browser connection verified")

        # Navigate to initial URL if specified
        initial_url = os.getenv("BROWSER_URL")
        if initial_url:
            await send_progress(95, f"Navigating to {initial_url}")
            await playwright_tool.navigate(initial_url)

        await send_progress(100, "Remote browser environment ready!")

    except Exception as e:
        if progress_token and session:
            await session.send_progress_notification(
                progress_token=progress_token,
                progress=0,
                total=100,
                message=f"Initialization failed: {str(e)}",
            )
        raise


# Create FastMCP instance
mcp = FastMCP(
    name="HUD Remote Browser Environment",
    instructions="""
    This is a remote browser automation environment that connects to cloud browser providers.
    Use the playwright tool to interact with the browser.
    
    Available providers:
    - anchorbrowser: AnchorBrowser cloud browser service
    - browserbase: BrowserBase cloud browser service
    - steel: Steel browser automation platform
    - hyperbrowser: HyperBrowser cloud browser service
    - kernel: Kernel browser-as-a-service platform
    
    The browser provider is configured via the BROWSER_PROVIDER environment variable.
    """,
)


# Setup tool
@mcp.tool()
async def setup(
    function: str = Field(
        None,
        description="Setup function name. Available: navigate_to_url, set_cookies, clear_cookies, click_element, type_text, wait_for_element, sheets_from_xlsx, sheets_from_bytes, load_html_content",
    ),
    args: dict = Field(
        None,
        description="Arguments for the setup function. Each function has specific requirements - check the setup registry for details",
    ),
    name: str = Field(None, description="Problem name to lookup setup from problem registry"),
    ctx: Context = None,
) -> dict:
    """Setup the remote browser environment.

    Available setup functions:
    - navigate_to_url: Navigate to a URL (args: {url: str})
    - set_cookies: Set browser cookies (args: {cookies: list})
    - clear_cookies: Clear all browser cookies
    - click_element: Click an element (args: {selector: str})
    - type_text: Type text in an element (args: {selector: str, text: str})
    - wait_for_element: Wait for element to appear (args: {selector: str, timeout?: int})
    - sheets_from_xlsx: Load Google Sheets from XLSX file (args: {path: str})
    - sheets_from_bytes: Load Google Sheets from bytes (args: {data: str, filename: str})
    - load_html_content: Load HTML content directly (args: {html: str})

    Returns a dict with status, message, and any function-specific data.
    """
    return await setup_tool(function, args, name, ctx, browser_provider, playwright_tool)


# Evaluate tool
@mcp.tool()
async def evaluate(
    function: str = Field(
        None,
        description="Evaluator function name. Available: url_match, page_contains, cookie_exists, cookie_match, history_length, raw_last_action_is, selector_history, sheet_contains, sheets_cell_values, verify_type_action",
    ),
    args: dict = Field(
        None,
        description="Arguments for the evaluator function. Each evaluator has specific requirements - check the evaluator registry for details",
    ),
    name: str = Field(None, description="Problem name to lookup evaluation from problem registry"),
    ctx: Context = None,
) -> dict:
    """Evaluate the remote browser environment state.

    Available evaluator functions:
    - url_match: Check if current URL matches pattern (args: {target_url: str})
    - page_contains: Check if page contains text (args: {search_terms: str|list, partial_rewarding?: bool})
    - cookie_exists: Check if cookie exists (args: {name: str})
    - cookie_match: Check if cookie value matches (args: {name: str, value: str})
    - history_length: Check navigation history length (args: {expected_length: int})
    - raw_last_action_is: Check last action type (args: {expected_action: str})
    - selector_history: Get selector interaction history
    - sheet_contains: Check if sheet contains text (args: {text: str})
    - sheets_cell_values: Check cell values in sheets (args: {expected_values: dict})
    - verify_type_action: Verify text was typed (args: {expected_text: str})

    Returns evaluation result with reward, done, and info fields.
    """
    return await evaluate_tool(function, args, name, ctx, browser_provider, playwright_tool)


# MCP Resources
@mcp.resource("evaluators://registry")
async def get_evaluators_resource() -> str:
    """MCP resource containing all available evaluators."""
    return EvaluatorRegistry.to_json()


@mcp.resource("setup://registry")
async def get_setup_resource() -> str:
    """MCP resource containing all available setup functions."""
    return SetupRegistry.to_json()


@mcp.resource("problems://registry")
async def get_problems_resource() -> str:
    """MCP resource containing all available problem definitions."""
    return ProblemRegistry.to_json()


@mcp.resource("telemetry://live")
async def get_telemetry_live() -> str:
    """Live telemetry data for the remote browser environment."""
    import json
    from datetime import datetime

    telemetry_data = {
        "live_url": browser_provider.get_live_view_url() if browser_provider else None,
        "instance_id": browser_provider._instance_id if browser_provider else None,
        "provider": browser_provider.__class__.__name__ if browser_provider else None,
        "status": "ready" if browser_provider and browser_provider.is_running else "not_ready",
        "timestamp": datetime.now().isoformat(),
        "browser_connected": playwright_tool._browser.is_connected()
        if playwright_tool and playwright_tool._browser
        else False,
        "cdp_url": browser_provider.cdp_url if browser_provider else None,
    }

    # Add current page URL if available
    if playwright_tool and playwright_tool._page:
        try:
            telemetry_data["current_url"] = playwright_tool._page.url
        except Exception:
            telemetry_data["current_url"] = None

    return json.dumps(telemetry_data, indent=2)


# Cleanup on shutdown
async def cleanup():
    """Clean up resources on shutdown."""
    global browser_provider, playwright_tool, browser_computer

    logger.info("Cleaning up remote browser environment...")

    if playwright_tool and playwright_tool._browser:
        try:
            await playwright_tool._browser.close()
        except Exception as e:
            logger.error(f"Error closing playwright browser: {e}")

    if browser_provider:
        try:
            await browser_provider.close()
        except Exception as e:
            logger.error(f"Error closing browser provider: {e}")

    browser_provider = None
    playwright_tool = None


if __name__ == "__main__":
    import typer

    app = typer.Typer()

    @app.command()
    def run(transport: Literal["stdio", "streamable-http"] = "stdio"):
        """Run the MCP server."""
        mcp.run(transport=transport)

    app()
