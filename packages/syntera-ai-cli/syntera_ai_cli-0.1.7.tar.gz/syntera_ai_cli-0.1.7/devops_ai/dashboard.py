from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.prompt import Prompt
from datetime import datetime
import sys
import select
import threading
import time
from typing import Dict, Callable, Tuple, Optional

from .ui.panels import (
    create_header,
    create_tools_panel,
    create_content_panel,
    create_footer,
    create_input_panel,
    create_result_table
)
from .ui.tool_handlers import ToolHandlers
from .core import DevOpsAITools

if sys.platform != 'win32':
    import tty
    import termios
else:
    tty = None
    termios = None


class CrossPlatformInput:
    """Cross-platform keyboard input handler."""
    
    def __init__(self):
        self.key_queue = []
        self.running = True
        
        # Platform-specific setup
        if sys.platform == "win32":
            import msvcrt
            self.get_key = self._get_key_windows
        else:
            # Unix-like systems (Linux, macOS)
            try:
                self.old_settings = termios.tcgetattr(sys.stdin)
                self.get_key = self._get_key_unix
            except:
                # Fallback for environments where termios doesn't work
                self.get_key = self._get_key_fallback
    
    def _get_key_windows(self) -> Optional[str]:
        """Windows-specific key reading."""
        import msvcrt
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if key == b'\xe0':  # Special keys
                key = msvcrt.getch()
                if key == b'H':  # Up arrow
                    return "KEY_UP"
                elif key == b'P':  # Down arrow
                    return "KEY_DOWN"
            elif key == b'\r':  # Enter
                return "\r"
            elif key == b'q':
                return "q"
            elif key.isdigit() and b'1' <= key <= b'3':
                return key.decode()
        return None
    
    def _get_key_unix(self) -> Optional[str]:
        """Unix-like systems key reading."""
        try:
            tty.setraw(sys.stdin.fileno())
            if select.select([sys.stdin], [], [], 0.1)[0]:
                key = sys.stdin.read(1)
                if key == '\x1b':  # Escape sequence
                    if select.select([sys.stdin], [], [], 0.1)[0]:
                        key += sys.stdin.read(1)
                        if key == '\x1b[':
                            if select.select([sys.stdin], [], [], 0.1)[0]:
                                key += sys.stdin.read(1)
                                if key == '\x1b[A':  # Up arrow
                                    return "KEY_UP"
                                elif key == '\x1b[B':  # Down arrow
                                    return "KEY_DOWN"
                elif key == '\r' or key == '\n':  # Enter
                    return "\r"
                elif key == 'q':
                    return "q"
                elif key.isdigit() and '1' <= key <= '3':
                    return key
            return None
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)
    
    def _get_key_fallback(self) -> Optional[str]:
        """Fallback method using input() for environments where termios doesn't work."""
        # This is a simple fallback - in practice you might want to implement
        # a more sophisticated solution
        return None
    
    def cleanup(self):
        """Cleanup resources."""
        if hasattr(self, 'old_settings') and sys.platform != "win32":
            try:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)
            except:
                pass


class TextDashboard:
    """An enhanced text-based dashboard for SynteraAI DevOps with cross-platform keyboard navigation."""

    def __init__(self):
        self.console = Console()
        self.layout = Layout()
        self.devops_tools = DevOpsAITools()
        self.tool_handlers = ToolHandlers(self.devops_tools, self.console)
        self.input_handler = CrossPlatformInput()

        # Track active tool for highlighting
        self.active_tool_index = 0
        self.github_repo_url = None
        self.running = True

    def _display_result(self, result: str, title: str) -> None:
        """Display the result in a structured and visually appealing way."""
        result_group = create_result_table(result, title)
        self.layout["content"].update(create_content_panel(result_group))

    def run(self):
        """Run the dashboard with keyboard navigation and scrolling."""
        try:
            self.console.clear()

            # Setup layout structure
            self.layout.split_column(
                Layout(name="header", size=3),
                Layout(name="body", ratio=8),
                Layout(name="input", size=3),
                Layout(name="footer", size=2),
            )

            self.layout["body"].split_row(
                Layout(name="tools", ratio=1),
                Layout(name="content", ratio=3),
            )

            # Initial layout setup
            self.layout["header"].update(create_header())
            self.layout["tools"].update(self._render_tools_panel())
            self.layout["content"].update(create_content_panel())
            self.layout["input"].update(create_input_panel())
            self.layout["footer"].update(create_footer())

            # Prompt for GitHub repository URL at startup
            self.console.print("\n")
            self.github_repo_url = Prompt.ask(
                "[bold green]►[/bold green] [bold cyan]Enter the GitHub repository URL to work on[/bold cyan]",
                default="https://github.com/example/repo "
            )
            clone_output, self.local_repo_path = self.tool_handlers.set_repository(self.github_repo_url)
            if clone_output:
                self._display_result(clone_output, "Git Clone Output")

            handlers = {
                "1": self.tool_handlers.docker_generation,
                "2": self.tool_handlers.infrastructure,
                "3": self.tool_handlers.analyze_grafana_repo
            }

            # Start Live rendering
            with Live(self.layout, refresh_per_second=10, screen=True) as live:
                self.console.print("\n[yellow]Use arrow keys (↑↓) or j/k to navigate, Enter to select, 'q' to quit[/yellow]")
                time.sleep(1)  # Give user time to read instructions
                
                while self.running:
                    key = self.input_handler.get_key()

                    if key == "q":
                        break
                    elif key == "KEY_UP" or key == "k":
                        self.active_tool_index = max(0, self.active_tool_index - 1)
                    elif key == "KEY_DOWN" or key == "j":
                        self.active_tool_index = min(2, self.active_tool_index + 1)  # 0-2 for 3 tools
                    
                    # Update only the tools panel with the current tool
                    if key in ["KEY_UP", "KEY_DOWN", "k", "j"]:
                        self.layout["tools"].update(self._render_tools_panel())
                        live.refresh()

                    if key == "\r":  # Enter key pressed
                        active_tool_key = str(self.active_tool_index + 1)
                        self.layout["input"].update(create_input_panel(f"Running {active_tool_key}..."))
                        live.refresh()

                        handler = handlers.get(active_tool_key)
                        if handler:
                            live.stop()
                            try:
                                result, title = handler()
                                live.start()
                                self._display_result(result, title)
                            except Exception as e:
                                live.start()
                                self._display_result(f"Error: {str(e)}", "Error")

                        self.layout["input"].update(create_input_panel())
                        live.refresh()
                    
                    # Direct tool selection with number keys
                    elif key and key.isdigit() and key in handlers:
                        self.active_tool_index = int(key) - 1
                        self.layout["tools"].update(self._render_tools_panel())
                        self.layout["input"].update(create_input_panel(f"Running {key}..."))
                        live.refresh()

                        handler = handlers.get(key)
                        if handler:
                            live.stop()
                            try:
                                result, title = handler()
                                live.start()
                                self._display_result(result, title)
                            except Exception as e:
                                live.start()
                                self._display_result(f"Error: {str(e)}", "Error")

                        self.layout["input"].update(create_input_panel())
                        live.refresh()

                    # Small sleep to prevent high CPU usage
                    time.sleep(0.05)

        except KeyboardInterrupt:
            self.console.print("\n[yellow]Dashboard interrupted by user[/yellow]")
        except Exception as e:
            self.console.print(f"\n[red]Dashboard error: {str(e)}[/red]")
        finally:
            self.input_handler.cleanup()

    def _render_tools_panel(self):
        tools = [
            {"key": "1", "icon": "🐳", "name": "Docker Generation", "desc": "Generate Docker and docker-compose files"},
            {"key": "2", "icon": "🏗️", "name": "Infrastructure", "desc": "Get infrastructure recommendations"},
            {"key": "3", "icon": "📈", "name": "Monitoring Audit", "desc": "Analyze Prometheus and Grafana configurations for observability, alerting, and visualization insights"}
        ]

        # Get the current tool
        current_tool = tools[self.active_tool_index]
        return create_tools_panel(current_tool)


# Alternative simpler approach using Rich's built-in prompt system
class SimplifiedDashboard:
    """A simplified dashboard that uses Rich's prompt system instead of raw keyboard input."""
    
    def __init__(self):
        self.console = Console()
        self.devops_tools = DevOpsAITools()
        self.tool_handlers = ToolHandlers(self.devops_tools, self.console)
        self.github_repo_url = None

    def run(self):
        """Run the simplified dashboard with menu selection."""
        self.console.clear()
        self.console.print("[bold blue]🚀 SynteraAI DevOps Dashboard[/bold blue]")
        self.console.print("=" * 50)

        # Prompt for GitHub repository URL at startup
        self.github_repo_url = Prompt.ask(
            "[bold green]►[/bold green] [bold cyan]Enter the GitHub repository URL to work on[/bold cyan]",
            default="https://github.com/example/repo"
        )
        
        clone_output, self.local_repo_path = self.tool_handlers.set_repository(self.github_repo_url)
        if clone_output:
            self.console.print(f"[green]Repository setup: {clone_output}[/green]")

        tools = {
            "1": ("🐳 Docker Generation", self.tool_handlers.docker_generation),
            "2": ("🏗️ Infrastructure", self.tool_handlers.infrastructure),
            "3": ("📈 Monitoring Audit", self.tool_handlers.analyze_grafana_repo),
            "q": ("❌ Quit", None)
        }

        while True:
            self.console.print("\n[bold yellow]Available Tools:[/bold yellow]")
            for key, (name, _) in tools.items():
                self.console.print(f"  {key}. {name}")

            choice = Prompt.ask(
                "\n[bold green]Select a tool (1-3) or 'q' to quit[/bold green]",
                choices=list(tools.keys()),
                default="q"
            )

            if choice == "q":
                break

            tool_name, handler = tools[choice]
            if handler:
                self.console.print(f"\n[blue]Running {tool_name}...[/blue]")
                try:
                    result, title = handler()
                    self.console.print(f"\n[bold green]{title}[/bold green]")
                    self.console.print(result)
                except Exception as e:
                    self.console.print(f"[red]Error: {str(e)}[/red]")
                
                input("\nPress Enter to continue...")


def main():
    """Main entry point for the dashboard."""
    # Try the cross-platform version first, fall back to simplified version
    try:
        dashboard = TextDashboard()
        dashboard.run()
    except Exception as e:
        print(f"Cross-platform dashboard failed: {e}")
        print("Falling back to simplified dashboard...")
        dashboard = SimplifiedDashboard()
        dashboard.run()


if __name__ == "__main__":
    main()