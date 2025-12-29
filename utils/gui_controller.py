"""
Simple Window API - Clean interface for window management
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from windowManager.window_functions import WindowController
from typing import Optional, Tuple, List, Dict

class SimpleWindowAPI:
    def __init__(self):
        self.controller = WindowController()
        self.controller.refresh_windows()
    
    # Window Discovery
    def get_windows(self) -> Dict:
        """Get all windows - returns clean dictionary"""
        self.controller.refresh_windows()
        return self.controller.window_lookup
    
    def find_window(self, title_contains: str, app_filter: str = None, refresh: bool = True) -> Optional[str]:
        """Find window by title - returns window ID or None"""
        if refresh:
            self.controller.refresh_windows(app_filter)
        
        search_term = title_contains.lower()
        for window_id, window_info in self.controller.window_lookup.items():
            title = window_info['window_data']['title'].lower()
            process = window_info['app_name'].lower()
            
            if search_term in title or search_term in process:
                return window_id
        return None
    
    def list_windows(self):
        """Print all windows with their IDs for easy discovery"""
        self.controller.print_windows_summary()
    
    # Window Control (return True/False for simplicity)
    def focus_window(self, window_id: str) -> bool:
        """Focus a window"""
        success, _ = self.controller._execute_single_command(f"{window_id} f")
        return success
    
    def close_window(self, window_id: str) -> bool:
        """Close a window"""
        success, _ = self.controller._execute_single_command(f"{window_id} c")
        return success
    
    def minimize_window(self, window_id: str) -> bool:
        """Minimize a window"""
        success, _ = self.controller._execute_single_command(f"{window_id} m")
        return success
    
    def maximize_window(self, window_id: str) -> bool:
        """Maximize a window"""
        success, _ = self.controller._execute_single_command(f"{window_id} M")
        return success
    
    def resize_window(self, window_id: str, width: int, height: int) -> bool:
        """Resize a window"""
        success, _ = self.controller._execute_single_command(f"{window_id} resize {width} {height}")
        return success
    
    def move_window(self, window_id: str, x: int, y: int) -> bool:
        """Move a window"""
        success, _ = self.controller._execute_single_command(f"{window_id} move {x} {y}")
        return success
    
    def move_window_to_monitor(self, window_id: str, monitor_id: int) -> bool:
        """Move window to specific monitor"""
        success, _ = self.controller._execute_single_command(f"{window_id} monitor {monitor_id}")
        return success
    
    # Mouse Control
    def click(self, x: int = None, y: int = None, button: str = "left") -> bool:
        """Click at position (or current cursor if no position)"""
        if x is not None and y is not None:
            success, _ = self.controller._execute_single_command(f"click {button} {x} {y}")
        else:
            success, _ = self.controller._execute_single_command(f"click {button}")
        return success
    
    def double_click(self, x: int = None, y: int = None, button: str = "left") -> bool:
        """Double click at position"""
        if x is not None and y is not None:
            success, _ = self.controller._execute_single_command(f"doubleclick {button} {x} {y}")
        else:
            success, _ = self.controller._execute_single_command(f"doubleclick {button}")
        return success
    
    def long_click(self, duration: float = 1.0, x: int = None, y: int = None, button: str = "left") -> bool:
        """Long click (hold) at position"""
        if x is not None and y is not None:
            success, _ = self.controller._execute_single_command(f"longclick {button} {duration} {x} {y}")
        else:
            success, _ = self.controller._execute_single_command(f"longclick {button} {duration}")
        return success
    
    def drag(self, start_x: int, start_y: int, end_x: int, end_y: int, button: str = "left", duration: float = 0.5) -> bool:
        """Drag from start to end position"""
        success, _ = self.controller._execute_single_command(f"drag {start_x} {start_y} {end_x} {end_y} {button} {duration}")
        return success
    
    def scroll(self, direction: str, amount: int = 3, x: int = None, y: int = None) -> bool:
        """Scroll up/down/left/right"""
        if x is not None and y is not None:
            success, _ = self.controller._execute_single_command(f"scroll {direction} {amount} {x} {y}")
        else:
            success, _ = self.controller._execute_single_command(f"scroll {direction} {amount}")
        return success
    
    # Keyboard Control
    def type_text(self, text: str) -> bool:
        """Type text"""
        success, _ = self.controller._execute_single_command(f"type {text}")
        return success
    
    def send_keys(self, keys: str) -> bool:
        """Send key combination (e.g., 'ctrl+c', 'alt+tab')"""
        success, _ = self.controller._execute_single_command(f"send {keys}")
        return success
    
    # Cursor Control
    def get_cursor_position(self) -> Optional[Tuple[int, int]]:
        """Get current cursor position"""
        success, message, pos = self.controller.wm.get_cursor_position()
        return pos if success else None
    
    def set_cursor_position(self, x: int, y: int) -> bool:
        """Set cursor position"""
        success, _ = self.controller._execute_single_command(f"cursor {x} {y}")
        return success
    
    # Introspection and Detection
    def inspect_cursor(self) -> Tuple[bool, str]:
        """Inspect element under cursor"""
        return self.controller._handle_introspection_command()
    
    def inspect_window(self, window_id: str) -> Tuple[bool, str]:
        """Inspect specific window"""
        if window_id not in self.controller.window_lookup:
            return False, f"Window ID '{window_id}' not found"
        
        window_info = self.controller.window_lookup[window_id]
        hwnd = window_info['window_data']['hwnd']
        return self.controller._handle_introspection_command(hwnd)
    
    def get_window_hierarchy(self, window_id: str) -> Tuple[bool, str]:
        """Get window hierarchy tree"""
        success, _ = self.controller._execute_single_command(f"{window_id} tree")
        return success
    
    # System Information
    def get_computer_name(self) -> str:
        """Get computer name"""
        success, message = self.controller._execute_single_command("computer")
        return message if success else ""
    
    def get_user_name(self) -> str:
        """Get current user name"""
        success, message = self.controller._execute_single_command("user")
        return message if success else ""
    
    # Application Launcher
    def launch_app(self, app_name: str, screen_id: int, fullscreen: bool = True) -> bool:
        """Launch application on specific screen"""
        mode = "fullscreen" if fullscreen else "normal"
        success, _ = self.controller._execute_single_command(f"launch {app_name} {screen_id} {mode}")
        return success
    
    # Message Box
    def show_message(self, title: str, message: str, x: int = None, y: int = None) -> bool:
        """Show message box"""
        if x is not None and y is not None:
            success, _ = self.controller._execute_single_command(f"msgbox {title} {message} {x} {y}")
        else:
            success, _ = self.controller._execute_single_command(f"msgbox {title} {message}")
        return success
    
    # Command Chaining
    def execute_chain(self, commands: List[str]) -> bool:
        """Execute a chain of commands"""
        command_string = " : ".join(commands)
        continue_running, message = self.controller.process_command(command_string)
        print(message)  # Print the chain execution results
        return continue_running
    
    # Utility Methods
    def get_window_info(self, window_id: str) -> Optional[Dict]:
        """Get detailed window information"""
        if window_id in self.controller.window_lookup:
            return self.controller.window_lookup[window_id]
        return None
    
    def get_window_state(self, window_id: str) -> Optional[str]:
        """Get window state (minimized, maximized, normal)"""
        if window_id not in self.controller.window_lookup:
            return None
        
        window_info = self.controller.window_lookup[window_id]
        hwnd = window_info['window_data']['hwnd']
        return self.controller.wm.get_window_state(hwnd)
    
    def get_window_position(self, window_id: str) -> Optional[Tuple[int, int]]:
        """Get window position"""
        info = self.get_window_info(window_id)
        if info:
            pos = info['window_data']['position']
            return (pos['x'], pos['y'])
        return None
    
    def get_window_size(self, window_id: str) -> Optional[Tuple[int, int]]:
        """Get window size"""
        info = self.get_window_info(window_id)
        if info:
            size = info['window_data']['size']
            return (size['width'], size['height'])
        return None
    
    def refresh(self, app_filter: str = None):
        """Refresh window list"""
        self.controller.refresh_windows(app_filter)
    
    def send_esc_enhanced(self) -> bool:
        """Enhanced ESC key for dialogs and modal windows"""
        success, _ = self.controller.wm.send_esc_enhanced()
        return success

# Convenience function for quick access
def get_window_api() -> SimpleWindowAPI:
    """Get a SimpleWindowAPI instance"""
    return SimpleWindowAPI()

# Quick test function
def quick_test():
    """Quick test to verify the API works"""
    print("🚀 Testing Simple Window API...")
    api = get_window_api()
    
    # List available windows
    print("\n📋 Available Windows:")
    api.list_windows()
    
    # Get cursor position
    pos = api.get_cursor_position()
    print(f"\n🖱️ Current cursor position: {pos}")
    
    # Get system info
    computer = api.get_computer_name()
    user = api.get_user_name()
    print(f"\n💻 System: {computer} (User: {user})")
    
    print("\n✅ Simple Window API is working!")

if __name__ == "__main__":
    quick_test()
