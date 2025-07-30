# -*- coding: utf-8 -*-
"""
此文件定义了所有可供 Executor 调用的工具。
每个工具都应是一个独立的类，包含一个 `execute` 方法。
"""
from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseTool(ABC):
    """
    所有工具的抽象基类。
    """
    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """
        执行工具的具体逻辑。

        Returns:
            Any: 工具执行后返回的原始数据（例如，网页HTML，API响应的JSON）。
        """
        pass

class WebSearchTool(BaseTool):
    """
    模拟一个网页搜索工具。
    """
    def execute(self, query: str, **kwargs) -> str:
        """
        执行搜索并返回模拟的网页内容。

        Args:
            query (str): 搜索查询。

        Returns:
            str: 模拟的搜索结果，例如一个很长的HTML文本。
        """
        print(f"WebSearchTool: Searching for '{query}'...")
        # 实际实现将调用搜索引擎API
        return f"<html><body><h1>Search Results for {query}</h1><p>This is a very long text representing the content of the searched page...</p></body></html>"

class StructuredDataAPITool(BaseTool):
    """
    模拟一个用于获取结构化数据的API工具。
    """
    def execute(self, endpoint: str, params: Dict = None, **kwargs) -> Dict:
        """
        调用API并返回模拟的JSON响应。

        Args:
            endpoint (str): API的端点。
            params (Dict, optional): API请求的参数。

        Returns:
            Dict: 模拟一个体积庞大的JSON响应。
        """
        print(f"StructuredDataAPITool: Calling endpoint '{endpoint}' with params {params}...")
        # 实际实现将使用 requests 或 httpx 等库
        return {
            "metadata": {"source": endpoint, "count": 1000},
            "data": [
                {"id": i, "value": f"record_{i}"} for i in range(1000)
            ]
        }

class ToolRegistry:
    """
    一个简单的注册表，用于管理和查找所有可用的工具。
    """
    def __init__(self):
        self._tools = {
            "web_search": WebSearchTool(),
            "structured_data_api": StructuredDataAPITool(),
        }

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
