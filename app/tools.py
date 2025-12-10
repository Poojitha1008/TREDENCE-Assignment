"""
Tool registry for workflow nodes.
Nodes can call registered tools to perform actions.
"""

from typing import Any, Callable, Dict
import logging

logger = logging.getLogger(__name__)


class ToolRegistry:
    """
    Registry for tools (Python functions) that workflow nodes can call.
    Tools are simple functions that take input and return output.
    """

    def __init__(self):
        self.tools: Dict[str, Callable[..., Any]] = {}

    def register(self, name: str, fn: Callable[..., Any]) -> None:
        """Register a tool."""
        if name in self.tools:
            logger.warning(f"Tool '{name}' is being overwritten")
        self.tools[name] = fn
        logger.info(f"Registered tool: {name}")

    def get(self, name: str) -> Callable[..., Any]:
        """Get a tool by name."""
        if name not in self.tools:
            raise ValueError(f"Tool '{name}' not registered")
        return self.tools[name]

    def call(self, name: str, **kwargs) -> Any:
        """Call a tool with keyword arguments."""
        fn = self.get(name)
        return fn(**kwargs)

    def list_tools(self) -> Dict[str, str]:
        """List all registered tools."""
        return {
            name: fn.__doc__ or "No description" for name, fn in self.tools.items()
        }

    def exists(self, name: str) -> bool:
        """Check if a tool is registered."""
        return name in self.tools
