import os
import subprocess
import sys
from pathlib import Path
import click
import uvicorn
from ..server.app import AgentServer
from ..utils.yaml_parser import ConfigParser

@click.command()
@click.option('-p', '--port', default=8000, help='Port to serve on')
@click.option('-f', '--file', default='agent.yaml', help='Agent configuration file')
@click.option('--host', default='0.0.0.0', help='Host to bind to')
@click.option('--skip-setup', is_flag=True, help='Skip virtual environment setup and dependency installation')
@click.option('--reload', is_flag=True, help='Enable auto-reload on code changes (development mode)')
def serve_command(port: int, file: str, host: str, skip_setup: bool, reload: bool) -> None:
    """Serve agent locally"""
    try:
        if not skip_setup:
            _setup_project(file)
            _activate_venv()
        
        # TODO: to pass debug mode to the server
        if reload:
            click.echo(f"Starting agent server on {host}:{port} with auto-reload enabled")
            # For reload mode, we need to pass the app factory to uvicorn
            # Set environment variable so the app factory can find the config
            os.environ['DEFINABLE_CONFIG_FILE'] = file
            
            # Import and run with reload
            import definable.server.main
            uvicorn.run(
                "definable.server.main:create_app",
                host=host, 
                port=port, 
                reload=True,
                reload_dirs=["."],  # Watch current directory for changes
                factory=True
            )
        else:
            server = AgentServer(file)
            click.echo(f"Starting agent server on {host}:{port}")
            uvicorn.run(server.app, host=host, port=port)
    except Exception as e:
        click.echo(f"Server failed to start: {e}", err=True)
        raise click.Abort()

def _setup_project(config_file: str) -> None:
    """Set up project: create venv, install deps, set environment variables"""
    click.echo("Setting up project environment...")
    
    # Load configuration
    try:
        config = ConfigParser.load_config(config_file)
    except Exception as e:
        click.echo(f"Failed to load config: {e}", err=True)
        raise click.Abort()
    
    # Create virtual environment if it doesn't exist
    venv_path = Path(".venv")
    if not venv_path.exists():
        click.echo("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)
    else:
        click.echo("Virtual environment already exists")
    
    # Get python executable from venv
    if os.name == 'nt':  # Windows
        python_exec = venv_path / "Scripts" / "python.exe"
        pip_exec = venv_path / "Scripts" / "pip.exe"
    else:  # Unix/Linux/macOS
        python_exec = venv_path / "bin" / "python"
        pip_exec = venv_path / "bin" / "pip"
    
    # Upgrade pip in virtual environment
    click.echo("Upgrading pip...")
    subprocess.run([str(pip_exec), "install", "--upgrade", "pip"], check=True)
    
    # Install dependencies
    if config.build.dependencies:
        click.echo("Installing dependencies...")
        deps = config.build.dependencies
        # Install definable package itself if not in dependencies
        if not any("definable" in dep for dep in deps):
            deps.append("definable")
        subprocess.run([str(pip_exec), "install"] + deps, check=True)
    
    # Set environment variables in current process
    if config.build.environment_variables:
        click.echo("Setting environment variables...")
        for env_var in config.build.environment_variables:
            if "=" in env_var:
                key, value = env_var.split("=", 1)
                os.environ[key] = value
                click.echo(f"Set {key}=***")
    
    click.echo("Project setup complete!")

def _activate_venv() -> None:
    """Activate the virtual environment by updating sys.path"""
    venv_path = Path(".venv")
    
    if not venv_path.exists():
        click.echo("Virtual environment not found, skipping activation")
        return
    
    # Add virtual environment's site-packages to sys.path
    if os.name == 'nt':  # Windows
        site_packages = venv_path / "Lib" / "site-packages"
    else:  # Unix/Linux/macOS
        site_packages = venv_path / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"
    
    if site_packages.exists():
        site_packages_str = str(site_packages)
        if site_packages_str not in sys.path:
            sys.path.insert(0, site_packages_str)
        click.echo("Virtual environment activated")
    else:
        click.echo("Warning: Could not find site-packages in virtual environment")

# Export for CLI registration
serve = serve_command