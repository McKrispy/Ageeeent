# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from typing import Any, Dict
from Tools.utils.web_search import WebSearchTool
from Tools.utils.base_tool import BaseTool

def get_tools():
    """
    返回一个包含所有可用工具及其元数据的字典。
    Key是工具的唯一编号 (Tool-ID)。
    """
    return {
        "T001": {"class": WebSearchTool, "name": "web_search"},
        # 未来可以添加更多工具, e.g.
        # "T002": {"class": CodeInterpreterTool, "name": "code_interpreter"},
    }

class ToolRegistry:
    """
    一个简单的注册表，用于管理和查找所有可用的工具。
    它现在返回工具的类，而不是实例。
    """
    def __init__(self):
        self._tools_map = get_tools()
        self._tools_by_name = {details["name"]: details["class"] for _, details in self._tools_map.items()}

    def get_tool_class(self, name: str) -> type[BaseTool]:
        """
        根据名称获取工具的类。
        Executor将负责实例化这个类。

        Args:
            name (str): 工具的名称。

        Returns:
            type[BaseTool]: 工具的类定义。
        
        Raises:
            ValueError: 如果找不到指定的工具。
        """
        tool_class = self._tools_by_name.get(name)
        if not tool_class:
            raise ValueError(f"Tool '{name}' not found in the registry.")
        return tool_class

    def list_tools(self) -> list:
        """返回所有可用工具的名称列表。"""
        return list(self._tools_by_name.keys())
