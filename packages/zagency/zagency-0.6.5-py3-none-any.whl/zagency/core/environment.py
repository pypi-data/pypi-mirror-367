"""
Environment base class for shared state management across agents.
TODO: @zamborg clean up
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable
import inspect
from zagency.core.base import Fabric


class Environment(ABC):
    """
    Base class for environments that agents can interact with.
    Environments hold state that can be shared across multiple agents.
    """
    def __init__(self, *args, **kwargs):
        self._state: Dict[str, Any] = {}
        self._agents: List["Agent"] = []
        self._fabric: Dict[str, Fabric] = self._discover_fabric()
    
    def register_agent(self, agent: "Agent"):
        """Register an agent with this environment."""
        if agent not in self._agents:
            self._agents.append(agent)
    
    def unregister_agent(self, agent: "Agent"):
        """Unregister an agent from this environment."""
        if agent in self._agents:
            self._agents.remove(agent)
    
    @abstractmethod
    def get_state(self, agent: Optional["Agent"] = None) -> Dict[str, Any]:
        """
        Get the current state of the environment.
        Can optionally filter state based on the requesting agent.
        """
        pass
    
    @abstractmethod
    def update_state(self, updates: Dict[str, Any], agent: Optional["Agent"] = None):
        """
        Update the environment state.
        Can optionally track which agent made the update.
        """
        pass
    
    def __getitem__(self, key: str) -> Any:
        """Allow dict-like access to state."""
        return self._state.get(key)
    
    def __setitem__(self, key: str, value: Any):
        """Allow dict-like setting of state."""
        self._state[key] = value
    
    def get_fabric(self) -> Dict[str, Fabric]:
        """
        Get the fabric methods available in this environment.
        Fabric methods are capabilities that agents can discover and use.
        Returns a dict of fabric name to Fabric objects with rich metadata.
        """
        return self._fabric.copy()
    
    def _discover_fabric(self) -> Dict[str, Fabric]:
        """Finds all methods decorated with @fabric and wraps them in Fabric objects."""
        fabric_methods = {}
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if hasattr(method, "_is_fabric"):
                fabric_obj = Fabric.from_method(method, name)
                fabric_methods[name] = fabric_obj
        return fabric_methods
