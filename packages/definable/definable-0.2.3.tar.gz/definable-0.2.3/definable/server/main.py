"""Main server entry point for containerized agents"""
import uvicorn
import os
import sys
from pathlib import Path
from .app import AgentServer

def _activate_venv():
    """Activate the virtual environment by updating sys.path"""
    venv_path = Path(".venv")
    
    if not venv_path.exists():
        return
    
    # Add virtual environment's site-packages to sys.path
    if os.name == 'nt':  # Windows
        site_packages = venv_path / "Lib" / "site-packages"
    else:  # Unix/Linux/macOS
        # Find the actual Python version directory in the venv
        lib_path = venv_path / "lib"
        if lib_path.exists():
            # Look for python* directories
            python_dirs = [d for d in lib_path.iterdir() if d.is_dir() and d.name.startswith("python")]
            if python_dirs:
                # Use the first (and typically only) python directory
                site_packages = python_dirs[0] / "site-packages"
            else:
                # Fallback to system version
                site_packages = venv_path / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"
        else:
            site_packages = venv_path / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"
    
    if site_packages.exists():
        site_packages_str = str(site_packages)
        if site_packages_str not in sys.path:
            sys.path.insert(0, site_packages_str)
        
        # Also add current directory to sys.path for local imports
        current_dir = str(Path.cwd())
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)

def create_app():
    """App factory for uvicorn with auto-reload support"""
    # Activate virtual environment for subprocess
    _activate_venv()
    
    config_file = os.getenv("DEFINABLE_CONFIG_FILE", os.getenv("AGENT_CONFIG", "agent.yaml"))
    server = AgentServer(config_file)
    return server.app

def main() -> None:
    """Start the agent server"""
    config_file = os.getenv("AGENT_CONFIG", "agent.yaml")
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    
    server = AgentServer(config_file)
    uvicorn.run(server.app, host=host, port=port)

if __name__ == "__main__":
    main()