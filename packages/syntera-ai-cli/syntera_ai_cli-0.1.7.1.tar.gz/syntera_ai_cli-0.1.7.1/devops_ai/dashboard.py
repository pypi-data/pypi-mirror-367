from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.prompt import Prompt

from typing import Dict, Callable, Tuple
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

import click  # ← Replaces `keyboard`


class TextDashboard:
    """Enhanced text-based dashboard for SynteraAI DevOps with click-based keyboard navigation."""

    def __init__(self):
        self.console = Console()
        self.layout = Layout()
        self.devops_tools = DevOpsAITools()
        self.tool_handlers = ToolHandlers(self.devops_tools, self.console)

        # Track active tool for highlighting
        self.active_tool_index = 0
        self.github_repo_url = None

    def _display_result(self, result: str, title: str) -> None:
        """Display the result in a structured and visually appealing way."""
        result_group = create_result_table(result, title)
        self.layout["content"].update(create_content_panel(result_group))

    def run(self):
        """Run the dashboard with click-based keyboard navigation."""
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
            default="https://github.com/example/repo"
        )
        clone_output, self.local_repo_path = self.tool_handlers.set_repository(self.github_repo_url)
        if clone_output:
            self._display_result(clone_output, "Git Clone Output")

        # Tool handlers map
        handlers = {
            "1": self.tool_handlers.docker_generation,
            "2": self.tool_handlers.infrastructure,
            "3": self.tool_handlers.analyze_grafana_repo
        }

        # Start Live rendering
        with Live(self.layout, refresh_per_second=10, screen=True) as live:
            while True:
                key = self._get_keypress()

                if key == "q":
                    break
                elif key == "up":
                    self.active_tool_index = max(0, self.active_tool_index - 1)
                elif key == "down":
                    self.active_tool_index = min(2, self.active_tool_index + 1)  # Only 3 tools
                elif key in handlers:
                    # Direct tool selection by number
                    self.layout["input"].update(create_input_panel(f"Running {key}..."))
                    live.refresh()

                    live.stop()  # Pause live to avoid flicker during long ops
                    result, title = handlers[key]()
                    live.start()

                    self._display_result(result, title)
                    self.layout["input"].update(create_input_panel())
                    live.refresh()

                # Always update tools panel to reflect active selection
                self.layout["tools"].update(self._render_tools_panel())
                live.refresh()

    def _render_tools_panel(self):
        tools = [
            {"key": "1", "icon": "🐳", "name": "Docker Generation", "desc": "Generate Docker and docker-compose files"},
            {"key": "2", "icon": "🏗️", "name": "Infrastructure", "desc": "Get infrastructure recommendations"},
            {"key": "3", "icon": "📈", "name": "Monitoring Audit", "desc": "Analyze Prometheus and Grafana configurations"}
        ]

        current_tool = tools[self.active_tool_index]
        return create_tools_panel(current_tool)

    def _get_keypress(self) -> str:
        """
        Read a single keypress and return normalized string.
        Returns: 'up', 'down', '1', '2', '3', 'q', '\r', etc.
        """
        char = click.getchar(True)  # True = echo off

        if char == '\x1b[A':   # Up arrow
            return "up"
        elif char == '\x1b[B':  # Down arrow
            return "down"
        elif char == '\r':      # Enter
            return "\r"
        elif char == 'q':
            return "q"
        elif char in '123':
            return char
        else:
            return ""  # Ignore invalid keys
def main():
    """Main entry point for the dashboard."""
    dashboard = TextDashboard()
    dashboard.run()


if __name__ == "__main__":
    main()

# from rich.console import Console
# from rich.layout import Layout
# from rich.live import Live
# from rich.prompt import Prompt, Confirm
# from rich.table import Table
# from rich.panel import Panel
# from rich.text import Text
# from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

# from typing import Dict, Callable, Tuple
# from .ui.panels import (
#     create_header,
#     create_tools_panel,
#     create_content_panel,
#     create_footer,
#     create_input_panel,
#     create_result_table
# )
# from .ui.tool_handlers import ToolHandlers
# from .core import DevOpsAITools

# import click


# class TextDashboard:
#     """Enhanced text-based dashboard for SynteraAI DevOps with click-based interface."""

#     def __init__(self):
#         self.console = Console()
#         self.devops_tools = DevOpsAITools()
#         self.tool_handlers = ToolHandlers(self.devops_tools, self.console)
#         self.github_repo_url = None
#         self.local_repo_path = None

#     def _display_result(self, result: str, title: str) -> None:
#         """Display the result in a structured and visually appealing way."""
#         table = Table(
#             title=title,
#             show_header=True,
#             header_style="bold magenta",
#             border_style="blue",
#             title_style="bold cyan"
#         )
#         table.add_column("Content", style="dim", width=80)
        
#         # Split the result into sections and format them
#         sections = result.split("\n\n")
#         for section in sections:
#             if section.strip():
#                 table.add_row(section.strip())
        
#         self.console.print(table)

#     def _show_welcome_screen(self):
#         """Display welcome screen with ASCII art and instructions."""
#         welcome_panel = Panel.fit(
#             Text.from_markup(
#                 "[bold cyan]🚀 SynteraAI DevOps Dashboard[/bold cyan]\n\n"
#                 "[dim]AI-powered DevOps automation and insights[/dim]\n\n"
#                 "[bold yellow]Features:[/bold yellow]\n"
#                 "• 🐳 Docker Generation\n"
#                 "• 🏗️ Infrastructure Recommendations\n"
#                 "• 📈 Monitoring & Observability Audit\n"
#                 "• 🔒 Security Analysis\n"
#                 "• ⚡ Performance Optimization\n\n"
#                 "[bold green]Ready to optimize your DevOps workflow![/bold green]"
#             ),
#             border_style="blue",
#             padding=(1, 2)
#         )
#         self.console.print(welcome_panel)

#     def _get_repository_info(self):
#         """Get repository information from user."""
#         self.console.print("\n[bold cyan]📂 Repository Setup[/bold cyan]")
        
#         self.github_repo_url = Prompt.ask(
#             "[bold green]►[/bold green] [bold cyan]Enter the GitHub repository URL to work on[/bold cyan]",
#             default="https://github.com/example/repo"
#         )
        
#         with Progress(
#             SpinnerColumn(),
#             TextColumn("[bold cyan]Setting up repository...[/bold cyan]"),
#             BarColumn(bar_width=40),
#             TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
#             expand=True
#         ) as progress:
#             task = progress.add_task("Processing", total=100)
#             progress.update(task, advance=20)
            
#             try:
#                 clone_output, self.local_repo_path = self.tool_handlers.set_repository(self.github_repo_url)
#                 progress.update(task, advance=60)
                
#                 if self.local_repo_path:
#                     progress.update(task, completed=100)
#                     self.console.print(f"\n[bold green]✅ Repository setup complete![/bold green]")
#                     self.console.print(f"[dim]Local path: {self.local_repo_path}[/dim]")
#                     if clone_output:
#                         self.console.print(f"[dim]Output: {clone_output}[/dim]")
#                 else:
#                     progress.update(task, completed=100)
#                     self.console.print(f"\n[bold red]❌ Repository setup failed![/bold red]")
#                     if clone_output:
#                         self.console.print(f"[dim]Error: {clone_output}[/dim]")
#             except Exception as e:
#                 progress.update(task, completed=100)
#                 self.console.print(f"\n[bold red]❌ Repository setup error: {str(e)}[/bold red]")

#     def _show_menu(self) -> str:
#         """Display the main menu and get user choice."""
#         self.console.print("\n" + "="*70)
#         self.console.print("[bold cyan]🛠️  Available Tools[/bold cyan]")
#         self.console.print("="*70)
        
#         options = [
#             ("1", "🐳", "Docker Generation", "Generate Docker and docker-compose files"),
#             ("2", "🏗️", "Infrastructure Suggestions", "Get AI-powered infrastructure recommendations"),
#             ("3", "📈", "Monitoring Audit", "Analyze Prometheus and Grafana configurations"),
#             ("4", "🔒", "Security Analysis", "Perform comprehensive security audit"),
#             ("5", "⚡", "Performance Optimization", "Get optimization recommendations"),
#             ("6", "📊", "Repository Analytics", "Analyze repository structure and dependencies"),
#             ("r", "🔄", "Change Repository", "Switch to a different repository"),
#             ("q", "🚪", "Quit", "Exit the dashboard")
#         ]
        
#         for key, icon, name, desc in options:
#             self.console.print(f"  [bold green]{key}[/bold green] {icon} [bold]{name}[/bold] - [dim]{desc}[/dim]")
        
#         self.console.print("="*70)
        
#         return Prompt.ask(
#             "[bold yellow]Select a tool[/bold yellow]",
#             choices=["1", "2", "3", "4", "5", "6", "r", "q"],
#             default="q"
#         )

#     def _run_docker_generation(self):
#         """Execute Docker generation tool."""
#         self.console.print("\n[bold cyan]🐳 Docker Generation[/bold cyan]")
        
#         with Progress(
#             SpinnerColumn(),
#             TextColumn("[bold cyan]Generating Docker files...[/bold cyan]"),
#             BarColumn(bar_width=40),
#             TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
#             expand=True
#         ) as progress:
#             task = progress.add_task("Processing", total=100)
#             progress.update(task, advance=10)
            
#             try:
#                 # Call the actual docker generation method
#                 progress.update(task, advance=30)
#                 result, title = self.tool_handlers.docker_generation()
#                 progress.update(task, advance=50)
#                 progress.update(task, completed=100)
#                 self._display_result(result, title)
#             except Exception as e:
#                 progress.update(task, completed=100)
#                 self._display_result(f"Error: {str(e)}", "🐳 Docker Generation Error")

#     def _run_infrastructure_suggestions(self):
#         """Execute infrastructure suggestions tool."""
#         self.console.print("\n[bold cyan]🏗️ Infrastructure Suggestions[/bold cyan]")
        
#         context = Prompt.ask(
#             "Enter additional context for infrastructure suggestions (optional)",
#             default=""
#         )
        
#         with Progress(
#             SpinnerColumn(),
#             TextColumn("[bold cyan]Generating infrastructure recommendations...[/bold cyan]"),
#             BarColumn(bar_width=40),
#             expand=True
#         ) as progress:
#             task = progress.add_task("Processing", total=100)
#             try:
#                 result, title = self.tool_handlers.infrastructure()
#                 progress.update(task, completed=100)
#                 self._display_result(result, title)
#             except Exception as e:
#                 progress.update(task, completed=100)
#                 self._display_result(f"Error: {str(e)}", "🏗️ Infrastructure Error")

#     def _run_monitoring_audit(self):
#         """Execute monitoring audit tool."""
#         self.console.print("\n[bold cyan]📈 Monitoring Audit[/bold cyan]")
        
#         with Progress(
#             SpinnerColumn(),
#             TextColumn("[bold cyan]Analyzing monitoring configurations...[/bold cyan]"),
#             BarColumn(bar_width=40),
#             expand=True
#         ) as progress:
#             task = progress.add_task("Processing", total=100)
#             try:
#                 result, title = self.tool_handlers.analyze_grafana_repo()
#                 progress.update(task, completed=100)
#                 self._display_result(result, title)
#             except Exception as e:
#                 progress.update(task, completed=100)
#                 self._display_result(f"Error: {str(e)}", "📈 Monitoring Audit Error")

#     def _run_security_analysis(self):
#         """Execute security analysis tool."""
#         self.console.print("\n[bold cyan]🔒 Security Analysis[/bold cyan]")
        
#         with Progress(
#             SpinnerColumn(),
#             TextColumn("[bold cyan]Performing security audit...[/bold cyan]"),
#             BarColumn(bar_width=40),
#             expand=True
#         ) as progress:
#             task = progress.add_task("Processing", total=100)
#             try:
#                 # Assuming there's a security analysis method
#                 result = self.devops_tools._security_scan(self.local_repo_path)
#                 progress.update(task, completed=100)
#                 self._display_result(result, "🔒 Security Analysis Results")
#             except Exception as e:
#                 progress.update(task, completed=100)
#                 self._display_result(f"Error: {str(e)}", "🔒 Security Analysis Error")

#     def _run_performance_optimization(self):
#         """Execute performance optimization tool."""
#         self.console.print("\n[bold cyan]⚡ Performance Optimization[/bold cyan]")
        
#         context = Prompt.ask(
#             "Enter context for optimization analysis (optional)",
#             default=""
#         )
        
#         with Progress(
#             SpinnerColumn(),
#             TextColumn("[bold cyan]Analyzing performance optimization opportunities...[/bold cyan]"),
#             BarColumn(bar_width=40),
#             expand=True
#         ) as progress:
#             task = progress.add_task("Processing", total=100)
#             try:
#                 result = self.devops_tools._optimize(context or self.local_repo_path)
#                 progress.update(task, completed=100)
#                 self._display_result(result, "⚡ Performance Optimization Results")
#             except Exception as e:
#                 progress.update(task, completed=100)
#                 self._display_result(f"Error: {str(e)}", "⚡ Performance Optimization Error")

#     def _run_repository_analytics(self):
#         """Execute repository analytics tool."""
#         self.console.print("\n[bold cyan]📊 Repository Analytics[/bold cyan]")
        
#         with Progress(
#             SpinnerColumn(),
#             TextColumn("[bold cyan]Analyzing repository structure...[/bold cyan]"),
#             BarColumn(bar_width=40),
#             expand=True
#         ) as progress:
#             task = progress.add_task("Processing", total=100)
#             try:
#                 # Create a simple repository analysis
#                 import os
#                 import subprocess
                
#                 analytics = []
                
#                 if self.local_repo_path and os.path.exists(self.local_repo_path):
#                     # Count files by extension
#                     file_counts = {}
#                     for root, dirs, files in os.walk(self.local_repo_path):
#                         for file in files:
#                             ext = os.path.splitext(file)[1].lower()
#                             file_counts[ext] = file_counts.get(ext, 0) + 1
                    
#                     analytics.append("📁 File Distribution:")
#                     for ext, count in sorted(file_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
#                         analytics.append(f"  {ext or 'no extension'}: {count} files")
                    
#                     # Try to get git statistics
#                     try:
#                         os.chdir(self.local_repo_path)
#                         commit_count = subprocess.check_output(
#                             ["git", "rev-list", "--count", "HEAD"], 
#                             stderr=subprocess.DEVNULL
#                         ).decode().strip()
#                         analytics.append(f"\n📊 Git Statistics:")
#                         analytics.append(f"  Total commits: {commit_count}")
#                     except:
#                         analytics.append("\n📊 Git Statistics: Unable to fetch")
                
#                 result = "\n".join(analytics) if analytics else "No repository data available"
#                 progress.update(task, completed=100)
#                 self._display_result(result, "📊 Repository Analytics")
                
#             except Exception as e:
#                 progress.update(task, completed=100)
#                 self._display_result(f"Error: {str(e)}", "📊 Repository Analytics Error")

#     def run(self):
#         """Run the main dashboard loop."""
#         self.console.clear()
#         self._show_welcome_screen()
        
#         # Get repository information
#         self._get_repository_info()
        
#         # Main loop
#         while True:
#             choice = self._show_menu()
            
#             if choice == "q":
#                 self.console.print("\n[bold green]👋 Thank you for using SynteraAI DevOps Dashboard![/bold green]")
#                 break
#             elif choice == "r":
#                 self._get_repository_info()
#             elif choice == "1":
#                 self._run_docker_generation()
#             elif choice == "2":
#                 self._run_infrastructure_suggestions()  
#             elif choice == "3":
#                 self._run_monitoring_audit()
#             elif choice == "4":
#                 self._run_security_analysis()
#             elif choice == "5":
#                 self._run_performance_optimization()
#             elif choice == "6":
#                 self._run_repository_analytics()
            
#             # Ask if user wants to continue
#             if choice in ["1", "2", "3", "4", "5", "6"]:
#                 self.console.print()
#                 if not Confirm.ask("[bold yellow]Would you like to use another tool?[/bold yellow]", default=True):
#                     self.console.print("\n[bold green]👋 Thank you for using SynteraAI DevOps Dashboard![/bold green]")
#                     break


# def main():
#     """Main entry point for the dashboard."""
#     dashboard = TextDashboard()
#     dashboard.run()


# if __name__ == "__main__":
#     main()