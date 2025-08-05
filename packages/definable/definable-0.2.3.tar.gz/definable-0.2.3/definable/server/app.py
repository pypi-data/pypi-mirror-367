import importlib.util
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional, Type, cast

from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from ..base.agent import AgentBox
from ..base.models import AgentInfo
from ..utils.yaml_parser import ConfigParser


class AgentServer:
    def __init__(self, config_path: str = "agent.yaml"):
        self.config = ConfigParser.load_config(config_path)
        self.agent_instance: Optional[AgentBox] = None
        self.app = self._create_app()

    def _load_agent_class(self) -> AgentBox:
        """Dynamically load the agent class"""
        # Ensure virtual environment is activated before loading agent
        self._activate_venv()
        
        module_path, class_name = ConfigParser.get_agent_class_info(self.config.agent)

        # Load the module
        spec = importlib.util.spec_from_file_location("agent_module", module_path)
        if spec is None:
            raise ImportError(f"Could not load module spec from {module_path}")

        module = importlib.util.module_from_spec(spec)
        sys.modules["agent_module"] = module

        if spec.loader is None:
            raise ImportError(f"Module spec has no loader for {module_path}")

        spec.loader.exec_module(module)

        # Get the agent class and instantiate
        agent_class = cast(Type[AgentBox], getattr(module, class_name))
        agent_instance = agent_class()
        agent_instance._ensure_setup()

        return agent_instance

    def _create_app(self) -> FastAPI:
        """Create FastAPI application with agent endpoints"""
        app = FastAPI(
            title=f"{self.config.platform.name} Agent",
            description=self.config.platform.description,
            version=self.config.platform.version,
        )

        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Load agent instance
        self.agent_instance = self._load_agent_class()
        self.router = APIRouter()
        # Add routes
        self._add_routes()

        app.include_router(self.router)

        return app

    def _add_routes(self) -> None:
        """Add standardized agent routes with proper typing"""
        if self.agent_instance is None:
            raise RuntimeError("Agent instance not initialized")

        agent_name = self.config.platform.name

        @self.router.get("/health")
        async def health_check() -> Dict[str, Any]:
            return {"status": "healthy", "timestamp": time.time()}

        @self.router.get("/info", response_model=AgentInfo)
        async def get_agent_info() -> AgentInfo:
            if self.agent_instance is None:
                raise HTTPException(status_code=500, detail="Agent not initialized")
            return self.agent_instance.info()
        
        execution_methods = ["invoke"]  # Priority order
        implemented_method = None
        
        for method_name in execution_methods:
            if self.agent_instance._is_method_implemented(method_name):
                implemented_method = method_name
                break
        
        if implemented_method is None:
            raise ValueError(
                f"Agent {self.agent_instance.info().name} does not implement any execution methods"
            )

        # setup invoke endpoint
        controller_fn = getattr(self.agent_instance, implemented_method)
        if not callable(controller_fn):
            raise ValueError(
                f"Agent {self.agent_instance.info().name} does not have an '{implemented_method}' method"
            )

        self.router.add_api_route(
            path="/invoke",
            endpoint=controller_fn,
            methods=["POST"],
            summary="Invoke Agent",
            description=f"Invoke the {agent_name} agent with the specified input",
        )

    def _activate_venv(self) -> None:
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
