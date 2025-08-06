#!/usr/bin/env python3
"""CLI interface for GitHub Project MCP Server"""

import os
import sys
import json
import subprocess
import signal
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint
from dotenv import load_dotenv

console = Console()

def get_config_dir() -> Path:
    """Get the configuration directory"""
    config_home = os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
    return Path(config_home) / 'github-project-mcp'

def get_config_file() -> Path:
    """Get the configuration file path"""
    return get_config_dir() / 'config.json'

def load_config() -> dict:
    """Load configuration from file"""
    config_file = get_config_file()
    if config_file.exists():
        with open(config_file, 'r') as f:
            return json.load(f)
    return {}

def save_config(config: dict):
    """Save configuration to file"""
    config_dir = get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    
    config_file = get_config_file()
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)

@click.group()
@click.version_option(version="0.1.0", prog_name="github-project-mcp")
def cli():
    """GitHub Project MCP Server - Manage GitHub projects via GraphQL"""
    pass

@cli.command()
@click.option('--token', '-t', envvar='GITHUB_TOKEN', help='GitHub personal access token')
@click.option('--port', '-p', default=0, help='Port to run the server on (0 for stdio)')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--daemon', '-d', is_flag=True, help='Run as daemon/background process')
def start(token: Optional[str], port: int, verbose: bool, daemon: bool):
    """Start the GitHub Project MCP server"""
    
    # Load environment variables
    load_dotenv()
    
    # Check for token
    if not token:
        token = os.environ.get('GITHUB_TOKEN')
    
    if not token:
        # Try to load from config
        config = load_config()
        token = config.get('github_token')
    
    if not token:
        console.print("[red]Error:[/red] GitHub token not provided!")
        console.print("\nPlease provide a token using one of these methods:")
        console.print("1. Set GITHUB_TOKEN environment variable")
        console.print("2. Use --token flag")
        console.print("3. Configure with: gps config --token YOUR_TOKEN")
        sys.exit(1)
    
    # Set the token in environment for the server
    os.environ['GITHUB_TOKEN'] = token
    
    # Get the server module path
    server_path = Path(__file__).parent / 'server.py'
    
    if verbose:
        console.print(Panel.fit(
            f"[green]Starting GitHub Project MCP Server[/green]\n"
            f"Mode: {'stdio' if port == 0 else f'port {port}'}\n"
            f"Daemon: {daemon}",
            title="Server Status"
        ))
    
    try:
        if daemon:
            # Run as background process
            console.print("[green]🚀 Starting GitHub Project MCP Server in background...[/green]")
            if sys.platform == "win32":
                # Windows doesn't support fork, use subprocess
                subprocess.Popen(
                    [sys.executable, str(server_path)],
                    env=os.environ.copy(),
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
                )
                console.print("[green]✅ Server started successfully in background[/green]")
            else:
                # Unix-like systems
                pid = os.fork()
                if pid == 0:
                    # Child process
                    os.setsid()
                    subprocess.run([sys.executable, str(server_path)])
                    sys.exit(0)
                else:
                    # Parent process
                    console.print(f"[green]✅ Server started in background with PID: {pid}[/green]")
                    
                    # Save PID to file
                    pid_file = get_config_dir() / 'server.pid'
                    pid_file.parent.mkdir(parents=True, exist_ok=True)
                    pid_file.write_text(str(pid))
        else:
            # Run in foreground
            console.print("[green]🚀 Starting GitHub Project MCP Server...[/green]")
            console.print("[cyan]Server is running and ready to accept connections[/cyan]")
            console.print("[yellow]Press Ctrl+C to stop the server[/yellow]")
            subprocess.run([sys.executable, str(server_path)])
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Server stopped by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Error starting server:[/red] {e}")
        sys.exit(1)

@cli.command()
def stop():
    """Stop the running GitHub Project MCP server"""
    pid_file = get_config_dir() / 'server.pid'
    
    if not pid_file.exists():
        console.print("[yellow]No running server found[/yellow]")
        return
    
    try:
        pid = int(pid_file.read_text().strip())
        
        if sys.platform == "win32":
            subprocess.run(['taskkill', '/F', '/PID', str(pid)], check=True)
        else:
            os.kill(pid, signal.SIGTERM)
        
        pid_file.unlink()
        console.print("[green]Server stopped successfully[/green]")
    
    except ProcessLookupError:
        console.print("[yellow]Server process not found (may have already stopped)[/yellow]")
        pid_file.unlink()
    except Exception as e:
        console.print(f"[red]Error stopping server:[/red] {e}")

@cli.command()
def status():
    """Check the status of the GitHub Project MCP server"""
    pid_file = get_config_dir() / 'server.pid'
    
    table = Table(title="GitHub Project MCP Server Status")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")
    
    if pid_file.exists():
        try:
            pid = int(pid_file.read_text().strip())
            
            # Check if process is actually running
            if sys.platform == "win32":
                result = subprocess.run(['tasklist', '/FI', f'PID eq {pid}'], 
                                      capture_output=True, text=True)
                is_running = str(pid) in result.stdout
            else:
                try:
                    os.kill(pid, 0)
                    is_running = True
                except ProcessLookupError:
                    is_running = False
            
            if is_running:
                table.add_row("Status", "Running")
                table.add_row("PID", str(pid))
            else:
                table.add_row("Status", "Stopped (stale PID file)")
                pid_file.unlink()
        except Exception as e:
            table.add_row("Status", f"Error: {e}")
    else:
        table.add_row("Status", "Not running")
    
    # Check configuration
    config = load_config()
    if config.get('github_token'):
        table.add_row("GitHub Token", "Configured")
    else:
        table.add_row("GitHub Token", "Not configured")
    
    console.print(table)

@cli.command()
@click.option('--token', '-t', help='Set GitHub personal access token')
@click.option('--show', '-s', is_flag=True, help='Show current configuration')
@click.option('--clear', is_flag=True, help='Clear all configuration')
def config(token: Optional[str], show: bool, clear: bool):
    """Configure the GitHub Project MCP server"""
    
    if clear:
        config_file = get_config_file()
        if config_file.exists():
            config_file.unlink()
            console.print("[green]Configuration cleared[/green]")
        else:
            console.print("[yellow]No configuration to clear[/yellow]")
        return
    
    if show:
        config = load_config()
        if not config:
            console.print("[yellow]No configuration found[/yellow]")
            return
        
        table = Table(title="Current Configuration")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")
        
        for key, value in config.items():
            if key == 'github_token':
                # Mask the token
                masked_value = value[:4] + '*' * (len(value) - 8) + value[-4:] if len(value) > 8 else '*' * len(value)
                table.add_row("GitHub Token", masked_value)
            else:
                table.add_row(key, str(value))
        
        console.print(table)
        return
    
    if token:
        config = load_config()
        config['github_token'] = token
        save_config(config)
        console.print("[green]GitHub token configured successfully[/green]")
        return
    
    # Interactive configuration
    console.print("[bold cyan]GitHub Project MCP Server Configuration[/bold cyan]\n")
    
    config = load_config()
    
    # Get GitHub token
    current_token = config.get('github_token', '')
    if current_token:
        masked = current_token[:4] + '*' * (len(current_token) - 8) + current_token[-4:]
        console.print(f"Current token: {masked}")
        if not click.confirm("Do you want to update the token?"):
            return
    
    token = click.prompt("GitHub Personal Access Token", hide_input=True)
    config['github_token'] = token
    
    save_config(config)
    console.print("\n[green]Configuration saved successfully![/green]")

@cli.command()
def test():
    """Test the GitHub API connection"""
    load_dotenv()
    
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        config = load_config()
        token = config.get('github_token')
    
    if not token:
        console.print("[red]Error:[/red] No GitHub token configured")
        console.print("Run 'gps config --token YOUR_TOKEN' to configure")
        sys.exit(1)
    
    console.print("[cyan]Testing GitHub API connection...[/cyan]")
    
    import httpx
    import asyncio
    
    async def test_connection():
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        
        query = """
        query TestConnection {
            viewer {
                login
                name
                email
            }
        }
        """
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.github.com/graphql",
                    json={"query": query},
                    headers=headers,
                    timeout=10.0
                )
                response.raise_for_status()
                result = response.json()
                
                if "errors" in result:
                    console.print(f"[red]GraphQL Error:[/red] {result['errors']}")
                    return False
                
                user_data = result.get("data", {}).get("viewer", {})
                
                table = Table(title="GitHub Connection Test - Success!")
                table.add_column("Field", style="cyan")
                table.add_column("Value", style="green")
                
                table.add_row("Username", user_data.get("login", "N/A"))
                table.add_row("Name", user_data.get("name", "N/A"))
                table.add_row("Email", user_data.get("email", "N/A"))
                
                console.print(table)
                return True
        
        except httpx.HTTPStatusError as e:
            console.print(f"[red]HTTP Error:[/red] {e}")
            return False
        except Exception as e:
            console.print(f"[red]Connection Error:[/red] {e}")
            return False
    
    success = asyncio.run(test_connection())
    sys.exit(0 if success else 1)

@cli.command()
def tools():
    """List all available MCP tools"""
    tools_info = [
        ("list_issues", "List issues in a repository", "owner, repo, state"),
        ("create_issue", "Create a new issue", "owner, repo, title, body"),
        ("update_issue", "Update an existing issue", "issue_id, title, body, state"),
        ("delete_issue", "Close an issue", "issue_id"),
        ("list_projects", "List projects in a repository", "owner, repo"),
        ("get_project_items", "Get items in a project", "project_id"),
        ("get_repo_id", "Get repository ID", "owner, repo"),
    ]
    
    table = Table(title="Available MCP Tools")
    table.add_column("Tool Name", style="cyan", width=20)
    table.add_column("Description", style="white", width=40)
    table.add_column("Parameters", style="green", width=30)
    
    for name, description, params in tools_info:
        table.add_row(name, description, params)
    
    console.print(table)

@cli.command()
@click.argument('tool_name')
@click.argument('args', nargs=-1)
@click.option('--json-output', '-j', is_flag=True, help='Output results as JSON')
@click.option('--state', help='Issue state (OPEN/CLOSED)')
@click.option('--body', help='Issue body/description')
@click.option('--title', help='Issue title')
def query(tool_name: str, args: tuple, json_output: bool, state: Optional[str], 
          body: Optional[str], title: Optional[str]):
    """Execute a specific tool query directly
    
    Examples:
        gps query list_issues octocat hello-world
        gps query create_issue octocat hello-world --title "Bug" --body "Description"
        gps query update_issue ISSUE_ID --state CLOSED
    """
    
    load_dotenv()
    
    # Get token
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        config = load_config()
        token = config.get('github_token')
    
    if not token:
        console.print("[red]Error:[/red] No GitHub token configured")
        console.print("Run 'gps config --token YOUR_TOKEN' to configure")
        sys.exit(1)
    
    # Import the client
    from .server import GitHubGraphQLClient
    import asyncio
    
    async def run_query():
        client = GitHubGraphQLClient(token)
        
        try:
            result = None
            
            if tool_name == "list_issues":
                if len(args) < 2:
                    console.print("[red]Error:[/red] list_issues requires owner and repo arguments")
                    return
                owner, repo = args[0], args[1]
                result = await client.list_issues(owner, repo, state or "OPEN")
            
            elif tool_name == "create_issue":
                if len(args) < 2 or not title:
                    console.print("[red]Error:[/red] create_issue requires owner, repo, and --title")
                    return
                owner, repo = args[0], args[1]
                repo_id = await client.get_repository_id(owner, repo)
                result = await client.create_issue(repo_id, title, body)
            
            elif tool_name == "update_issue":
                if len(args) < 1:
                    console.print("[red]Error:[/red] update_issue requires issue_id")
                    return
                issue_id = args[0]
                result = await client.update_issue(issue_id, title, body, state)
            
            elif tool_name == "delete_issue":
                if len(args) < 1:
                    console.print("[red]Error:[/red] delete_issue requires issue_id")
                    return
                issue_id = args[0]
                success = await client.delete_issue(issue_id)
                result = {"success": success, "message": "Issue closed" if success else "Failed"}
            
            elif tool_name == "list_projects":
                if len(args) < 2:
                    console.print("[red]Error:[/red] list_projects requires owner and repo")
                    return
                owner, repo = args[0], args[1]
                result = await client.list_projects(owner, repo)
            
            elif tool_name == "get_project_items":
                if len(args) < 1:
                    console.print("[red]Error:[/red] get_project_items requires project_id")
                    return
                project_id = args[0]
                result = await client.get_project_items(project_id)
            
            elif tool_name == "get_repo_id":
                if len(args) < 2:
                    console.print("[red]Error:[/red] get_repo_id requires owner and repo")
                    return
                owner, repo = args[0], args[1]
                repo_id = await client.get_repository_id(owner, repo)
                result = {"repository_id": repo_id}
            
            else:
                console.print(f"[red]Error:[/red] Unknown tool: {tool_name}")
                console.print("Run 'gps tools' to see available tools")
                return
            
            # Output results
            if json_output:
                print(json.dumps(result, indent=2, default=str))
            else:
                if isinstance(result, list):
                    console.print(f"[green]Found {len(result)} items[/green]")
                    for item in result[:5]:  # Show first 5 items
                        if 'title' in item:
                            console.print(f"  • {item.get('number', 'N/A')}: {item['title']}")
                    if len(result) > 5:
                        console.print(f"  ... and {len(result) - 5} more")
                elif isinstance(result, dict):
                    for key, value in result.items():
                        console.print(f"[cyan]{key}:[/cyan] {value}")
                else:
                    console.print(result)
        
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            sys.exit(1)
    
    asyncio.run(run_query())

if __name__ == "__main__":
    cli()