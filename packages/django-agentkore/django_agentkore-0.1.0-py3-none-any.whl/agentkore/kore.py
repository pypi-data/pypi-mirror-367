"""
Django AI Agent Core Utilities

This module provides utility functions and base classes to work with AI agents in Django projects.
"""
import importlib
from pathlib import Path
from typing import Dict, Any, Optional, Type, List


class AgentRegistry:
    """
    A registry for managing AI agents within a Django project.
    """
    _agents = {}

    @classmethod
    def register(cls, name: str, agent_class: Type):
        """Register an agent class with the registry"""
        cls._agents[name] = agent_class

    @classmethod
    def get_agent(cls, name: str):
        """Get an agent class by name"""
        return cls._agents.get(name)

    @classmethod
    def list_agents(cls) -> List[str]:
        """List all registered agents"""
        return list(cls._agents.keys())


class BaseAgent:
    """
    Base class for Django AI agents.
    """

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}

    def run(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Execute the agent's main logic on the given prompt.

        Args:
            prompt: The user input to process
            context: Optional dictionary with additional context

        Returns:
            A string response from the agent
        """
        raise NotImplementedError("Subclasses must implement run()")

    def __str__(self):
        return f"{self.__class__.__name__}(name='{self.name}')"


def discover_agents(agents_dir: str = 'agents') -> Dict[str, Type]:
    """
    Automatically discover agent implementations in a Django project.

    Args:
        agents_dir: Directory name where agents are stored

    Returns:
        Dictionary mapping agent names to agent classes
    """
    agents = {}
    base_path = Path(agents_dir)

    if not base_path.exists():
        return agents

    for agent_dir in base_path.iterdir():
        if not agent_dir.is_dir() or agent_dir.name.startswith('_'):
            continue

        try:
            # Try to import the agent module
            module_path = f"{agents_dir}.{agent_dir.name}.agent"
            module = importlib.import_module(module_path)

            # Look for a class matching the expected pattern
            class_name = f"{agent_dir.name.capitalize()}Agent"
            agent_class = getattr(module, class_name, None)

            if agent_class:
                agents[agent_dir.name] = agent_class
                # Also register with the registry
                AgentRegistry.register(agent_dir.name, agent_class)
        except (ImportError, AttributeError):
            # Skip any directories that don't contain valid agents
            continue

    return agents
