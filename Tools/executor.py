# -*- coding: utf-8 -*-
"""
此文件定义了 Executor (执行器) 类。
执行器是连接规划和行动的桥梁，负责调用工具、协调数据流，
并严格遵守“原始数据存入RedisJSON，摘要存入MCP”的核心原则。
"""
from Data.mcp_models import MCP
from Interfaces.database_interface import RedisClient
from Interfaces.llm_api_interface import OpenAIInterface, GoogleCloudInterface
from Entities.filter_summary import LLMFilterSummary
from .tool_registry import ToolRegistry
import hashlib

class ToolExecutor:
    """
    执行器类，负责在运行时实例化和执行工具。
    它现在还将 RedisClient 的实例传递给它创建的每个工具。
    """
    def __init__(self, db_interface: RedisClient, llm_summarizer: LLMFilterSummary):
        self.db_interface = db_interface
        self.llm_summarizer = llm_summarizer
        self.tool_registry = ToolRegistry()
        self.entity_id = self.__class__.__name__

    def execute(self, mcp: MCP) -> MCP:
        """
        执行 MCP 中定义的命令。
        1. 从注册表获取工具类。
        2. 实例化工具，并将 RedisClient 实例和 LLMFilterSummary 实例传递给它。
        3. 执行工具。
        4. 工具执行后，它将自行处理数据存储和摘要生成。
        5. 从工具的执行结果中更新 MCP。
        """
        command = mcp.executable_command
        if not command:
            print("Executor Error: No executable command found in MCP.")
            return mcp

        tool_name = command.get("tool")
        tool_params = command.get("params", {})

        print(f"Executor: Executing tool '{tool_name}' with params: {tool_params}")

        if not tool_name:
            print("Executor Error: No tool specified in the command.")
            return mcp

        try:
            # 1. 从注册表获取工具类
            tool_class = self.tool_registry.get_tool_class(tool_name)
            
            # 2. 实例化工具，并传入 db_interface 和 llm_summarizer
            tool_instance = tool_class(
                db_interface=self.db_interface,
                llm_summarizer=self.llm_summarizer
            )
            
            print(f"Executor: Executing tool '{tool_instance.tool_id}' (Instance: {tool_instance.instance_id}) with params: {tool_params}")
            
            # 3. 执行工具，现在工具的 execute 方法需要 mcp 参数
            execution_result = tool_instance.execute(mcp, **tool_params)

            # 4. 根据工具返回的结果更新 MCP
            # 我们期望工具返回一个包含 'summary' 和 'data_key' 的字典
            if execution_result and isinstance(execution_result, dict):
                mcp.working_memory = {
                    "summary": execution_result.get("summary", ""),
                    "data_pointers": {
                        "raw_data_key": execution_result.get("data_key", ""),
                        "tool_instance_id": tool_instance.instance_id
                    }
                }
                print("Executor: Updated working memory based on tool's execution result.")
            else:
                print("Executor Warning: Tool did not return the expected dictionary. Working memory not updated.")

        except ValueError as e:
            print(f"Execution Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred during execution: {e}")

        return mcp

if __name__ == "__main__":
    llm_interface = GoogleCloudInterface()
    db_interface = RedisClient()
    executor = ToolExecutor(db_interface, LLMFilterSummary(llm_interface, db_interface))
    mcp = MCP(
    session_id="test_session_002",
    user_requirements="预测2030年中国人口"
)
    mcp.executable_command = {
        "tool": "web_search",
        "params": {
            "keywords": ["2030", "中国", "人口"]
        }
    }
    executor.execute(mcp)
    