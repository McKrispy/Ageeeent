# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from typing import Any, Dict
from Tools.utils.web_search import WebSearchTool
from Tools.utils.base_tool import BaseTool

TOOLS = {
    "web_search": WebSearchTool(),
}

class ToolRegistry:
    """
    一个简单的注册表，用于管理和查找所有可用的工具。
    """
    def __init__(self):
        self._tools = TOOLS

    def get_tool(self, name: str) -> BaseTool:
        """
        根据名称获取工具实例。

        Args:
            name (str): 工具的名称。

        Returns:
            BaseTool: 工具的实例。
        
        Raises:
            ValueError: 如果找不到指定的工具。
        """
        tool = self._tools.get(name)
        if not tool:
            raise ValueError(f"Tool '{name}' not found in the registry.")
        return tool

    def list_tools(self) -> list:
        """返回所有可用工具的名称列表。"""
        return list(self._tools.keys())
