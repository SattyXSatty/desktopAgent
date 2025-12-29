import os
import sys
import time
from typing import Dict, List, Optional
from mcp.server.fastmcp import FastMCP

# Add current directory and utils/fdom to path for imports
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "utils", "fdom"))

# ✅ CRITICAL: Force all Rich Console output to stderr to avoid polluting JSONRPC
from rich.console import Console
_original_init = Console.__init__
def _new_init(self, *args, **kwargs):
    if 'file' not in kwargs:
        kwargs['file'] = sys.stderr
    _original_init(self, *args, **kwargs)
Console.__init__ = _new_init

from utils.fdom.element_interactor import ElementInteractor

# Initialize FastMCP
mcp = FastMCP("ComputerInteractor")

# Global state to keep the interactor alive
class SessionState:
    interactor: Optional[ElementInteractor] = None
    app_path: str = ""

state = SessionState()

@mcp.tool()
def launch_app(app_path_or_name: str) -> str:
    """
    Launches an application and initializes the element interactor.
    Example: launch_app("/System/Applications/Calculator.app") or launch_app("Calculator")
    """
    try:
        # Correct path for common Mac apps if just name given
        if not app_path_or_name.startswith("/") and not app_path_or_name.startswith("~"):
            if app_path_or_name.lower() == "calculator":
                app_path_or_name = "/System/Applications/Calculator.app"
        
        state.interactor = ElementInteractor(app_path_or_name)
        state.app_path = app_path_or_name
        return f"✅ Successfully launched {app_path_or_name} and initialized UI tracking."
    except Exception as e:
        return f"❌ Failed to launch app: {str(e)}"

@mcp.tool()
def get_ui_state() -> str:
    """
    Returns the current UI state, including a list of interactable nodes.
    Each node has an ID, name, and description.
    """
    if not state.interactor:
        return "❌ Error: App not launched. Call launch_app first."
    
    try:
        # Refresh state if needed
        current_state_id = state.interactor.current_state_id
        fdom_data = state.interactor.state_manager.fdom_data
        nodes = fdom_data.get("states", {}).get(current_state_id, {}).get("nodes", {})
        
        if not nodes:
            return f"📍 Current State: {current_state_id}\n⚠️ No interactable nodes found in this state."
        
        response = [f"📍 Current State: {current_state_id}", "🟡 Available Nodes:"]
        for node_id, data in nodes.items():
            unique_id = f"{current_state_id}::{node_id}"
            name = data.get("g_icon_name", "unknown")
            g_type = data.get("g_type", "icon")
            description = data.get("g_brief", "")
            
            line = f"- [{unique_id}] {name} ({g_type})"
            if description:
                line += f": {description}"
            response.append(line)
            
        return "\n".join(response)
    except Exception as e:
        return f"❌ Error retrieving UI state: {str(e)}"

@mcp.tool()
def click_node(node_id: str) -> str:
    """
    Clicks a specific node by its full ID (e.g., 'root::1').
    """
    if not state.interactor:
        return "❌ Error: App not launched."
    
    try:
        result = state.interactor.click_element(node_id)
        if result.success:
            msg = f"✅ Clicked {node_id}."
            if result.state_changed:
                msg += f" UI changed to new state: {result.new_state_id}"
            else:
                msg += " No state change detected."
            return msg
        else:
            return f"❌ Click failed: {result.error_message}"
    except Exception as e:
        return f"❌ Exception during click: {str(e)}"

@mcp.tool()
def type_text(text: str) -> str:
    """
    Types text into the currently focused window or element.
    """
    if not state.interactor:
        return "❌ Error: App not launched."
    
    try:
        success = state.interactor.app_controller.gui_api.type_text(text)
        if success:
            # Type usually doesn't trigger immediate state change detection in interactor
            # but we can refresh the state manually if we want.
            return f"✅ Successfully typed: '{text}'"
        else:
            return "❌ Typing failed."
    except Exception as e:
        return f"❌ Exception during typing: {str(e)}"

@mcp.tool()
def go_back() -> str:
    """
    Navigates back to the previous UI state.
    """
    if not state.interactor:
        return "❌ Error: App not launched."
    
    try:
        success = state.interactor.navigation_engine.navigate_back_to_state(None) # None pops the stack
        if success:
            return f"✅ Navigated back. Current state is now {state.interactor.current_state_id}"
        else:
            return "❌ Failed to navigate back."
    except Exception as e:
        return f"❌ Exception during navigation: {str(e)}"

@mcp.tool()
def wait(seconds: float) -> str:
    """
    Waits for a specified amount of time.
    """
    time.sleep(seconds)
    return f"✅ Waited {seconds} seconds."

if __name__ == "__main__":
    mcp.run()
