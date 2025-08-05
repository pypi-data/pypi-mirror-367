from abc import ABC, abstractmethod
from typing import Any
import inspect

from fastapi.responses import JSONResponse, StreamingResponse

from .models import AgentInfo, AgentOutput


class AgentBox(ABC):
    """Base class for all agents - requires AgentInput/AgentOutput subclasses
    
    Required methods:
    - info(): Return agent information
    - At least ONE of: invoke(), ainvoke(), stream(), or astream()
    
    Optional methods (override as needed):
    - invoke(): Main synchronous entry point
    - ainvoke(): Async entry point
    - stream(): Streaming entry point
    - astream(): Async streaming entry point
    """

    def __init__(self) -> None:
        self._initialized = False

    def setup(self) -> None:
        """Override this method to initialize your agent"""
        pass

    # TODO : add pre and post hook middlewares
    def pre_hook(self) -> None:
        """Optional pre-processing hook"""
        pass

    def post_hook(self) -> None:
        """Optional post-processing hook"""
        pass

    def invoke(self, agent_input: Any) -> AgentOutput | JSONResponse:
        """Main entry point - implement your agent logic here

        Must use AgentInput and AgentOutput subclasses for proper API documentation
        """
        pass

    @abstractmethod
    def info(self) -> AgentInfo:
        """Return information about the agent"""
        pass

    def _ensure_setup(self) -> None:
        """Ensure setup is called once"""
        if not self._initialized:
            self.setup()
            self._initialized = True

    def _is_method_implemented(self, method_name: str) -> bool:
        """Check if a method is actually implemented by the agent"""
        method = getattr(self, method_name, None)
        if method is None or not callable(method):
            return False
            
        # Get the method from the base class for comparison
        base_method = getattr(AgentBox, method_name, None)
        if base_method is None:
            return False
            
        try:
            # Check if the method is overridden (different implementation than base class)
            agent_method_code = inspect.getsource(method)
            base_method_code = inspect.getsource(base_method)
            
            # If the source code is different, it's implemented
            return agent_method_code != base_method_code
        except (OSError, TypeError):
            # If we can't get source code, assume it's implemented if it exists
            return True

    def validate_implementation(self) -> None:
        """Validate that at least one agent method is implemented"""
        execution_methods = ["invoke", "ainvoke", "stream", "astream"]
        implemented_methods = []
        
        for method_name in execution_methods:
            if self._is_method_implemented(method_name):
                implemented_methods.append(method_name)
        
        if not implemented_methods:
            raise ValueError(
                f"Agent {self.__class__.__name__} must implement at least one of: "
                f"{', '.join(execution_methods)}. No execution methods found."
            )
        
        print(f"✓ Agent {self.__class__.__name__} implements: {', '.join(implemented_methods)}")
