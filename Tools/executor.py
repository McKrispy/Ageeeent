# -*- coding: utf-8 -*-
"""
此文件定义了 Executor (执行器) 类。
执行器是连接规划和行动的桥梁，负责调用工具、协调数据流，
并严格遵守"原始数据存入RedisJSON，摘要存入MCP"的核心原则。
"""
from sys import executable
import time
import threading
from typing import Dict, Any

from Data.mcp_models import MCP, WorkingMemory, ExecutableCommand
from Interfaces.database_interface import RedisClient
from Interfaces.llm_api_interface import OpenAIInterface, GoogleCloudInterface
from Entities.filter_summary import LLMFilterSummary
from .tool_registry import ToolRegistry
from concurrent.futures import ThreadPoolExecutor, as_completed

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

    def execute(
        self, mcp: MCP , working_memory: WorkingMemory
    ) -> bool:
        executable_commands = mcp.executable_commands

        if not executable_commands:
            print("Executor Error: No executable command provided.")
            return False

        with ThreadPoolExecutor(max_workers=len(executable_commands)) as executor:
            futures = []
            for cmd in executable_commands:
                tool_name = cmd.tool
                tool_params = cmd.params
                if not tool_name:
                    print(f"Executor Error: No tool name found for command: {cmd}")
                    continue
                if not tool_params:
                    print(f"Executor Error: No tool params found for command: {cmd}")
                    continue
                future = executor.submit(self._execute_single_cmd, mcp, cmd)
                futures.append(future)

            for future in as_completed(futures):
                result = future.result()
                if result:
                    working_memory.data.update(result)
                else:
                    print(f"Executor Error: Failed to execute command: {cmd}")
                    return False
            
        return True

    def _execute_single_cmd(self, mcp: MCP, cmd: ExecutableCommand):
        """
        执行单个entry的辅助方法，用于在线程池中调用
        """
        
        try:
            tool_class = self.tool_registry.get_tool_class(cmd.tool)
            tool_instance = tool_class(self.db_interface, self.llm_summarizer)
            return tool_instance.execute(mcp, cmd)
        except Exception as e:
            print(
                f"Executor Error in thread: Failed to execute entry for tool '{cmd.tool}' "
                f"(Instance: {cmd.tool}): {e}"
            )
            return None


if __name__ == "__main__":
    llm_interface = OpenAIInterface()
    db_interface = RedisClient()
    executor = ToolExecutor(db_interface, LLMFilterSummary(llm_interface))
    
    cmd_list = []
    for i in range(2020, 2030):
        cmd_list.append(ExecutableCommand(
            parent_sub_goal_id="test_sg_001",
            tool="web_search",
            params={
                "keywords": [f"{i}", "中国", "人口", "预测"],
                "num_results": 3,
            }
        ))

    mcp = MCP(
        session_id="test_session_002",
        user_requirements="Test user requirements",
        executable_commands=cmd_list
    )
    working_memory = WorkingMemory()
    executor.execute(mcp, working_memory)
    print(f"Executor: Working memory data: {working_memory.data}")
    
