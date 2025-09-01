# -*- coding: utf-8 -*-
from Tools.utils.web_search import WebSearchTool
from Tools.utils.base_tool import BaseTool

def get_tools():
    """
    Returns a dictionary containing all available tools and their metadata.
    Key is the unique identifier of the tool (Tool-ID).
    """
    return {
        "T001": {"class": WebSearchTool, "name": "web_search"},
        # More tools can be added in the future, e.g.
        # "T002": {"class": CodeInterpreterTool, "name": "code_interpreter"},
    }

class ToolRegistry:
    """
    A simple registry for managing and finding all available tools.
    It now returns tool classes instead of instances.
    """
    def __init__(self):
        self._tools_map = get_tools()
        self._tools_by_name = {details["name"]: details["class"] for _, details in self._tools_map.items()}

    def get_tool_class(self, name: str) -> type[BaseTool]:
        """
        Get tool class by name.
        Executor will be responsible for instantiating this class.

        Args:
            name (str): Name of the tool.

        Returns:
            type[BaseTool]: Tool class definition.
        
        Raises:
            ValueError: If the specified tool is not found.
        """
        tool_class = self._tools_by_name.get(name)
        if not tool_class:
            raise ValueError(f"Tool '{name}' not found in the registry.")
        return tool_class

    def list_tools(self) -> list:
        """Return a list of names of all available tools."""
        return list(self._tools_by_name.keys())
