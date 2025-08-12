# -*- coding: utf-8 -*-
"""
此文件定义了 Executor (执行器) 类。
执行器是连接规划和行动的桥梁，负责调用工具、协调数据流，
并严格遵守"原始数据存入RedisJSON，摘要存入MCP"的核心原则。
"""
import time
import threading

from Data.mcp_models import MCP, WorkingMemory
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
        self, mcp: MCP, working_memory: WorkingMemory
    ) -> tuple[MCP, WorkingMemory]:
        """
        执行 MCP 中定义的命令。
        1. 从注册表获取工具类。
        2. 为每个entry创建独立的工具实例，并将 RedisClient 实例和 LLMFilterSummary 实例传递给它。
        3. 并行执行工具。
        4. 工具执行后，它将自行处理数据存储和摘要生成。
        5. 从工具的执行结果中更新 MCP。
        """
        command = mcp.executable_command
        if not command:
            print("Executor Error: No executable command found in MCP.")
            return mcp, working_memory

        tools = command.get("tools")

        for tool in tools:
            tool_name = tool.get("tool")
            tool_params = tool.get("params", {})

            print(f"Executor: Executing tool '{tool_name}' with params: {tool_params}")

            try:
                # 1. 从注册表获取工具类
                tool_class = self.tool_registry.get_tool_class(tool_name)
                
                # 2. 获取所有entries
                entries = tool_params.get("entries", [])
                if not entries:
                    print(f"Executor: No entries found for tool '{tool_name}'")
                    continue

                # 3. 并行执行每个entry，为每个entry创建独立的tool_instance
                with ThreadPoolExecutor(max_workers=min(len(entries), 10)) as executor:
                    # 提交所有任务
                    future_to_entry = {}
                    for entry in entries:
                        time.sleep(0.2)
                        # 为每个entry创建独立的tool_instance
                        tool_instance = tool_class(
                            db_interface=self.db_interface, 
                            llm_summarizer=self.llm_summarizer
                        )
                        
                        # 提交任务到线程池
                        future = executor.submit(
                            self._execute_single_entry,
                            tool_instance,
                            mcp,
                            entry
                        )
                        future_to_entry[future] = (tool_instance, entry)

                    for future in as_completed(future_to_entry):
                        tool_instance, entry = future_to_entry[future]
                        try:
                            execution_result = future.result()
                            if execution_result and isinstance(execution_result, dict):
                                with threading.Lock():
                                    working_memory.data.update(execution_result)
                        except Exception as e:
                            print(f"Executor Error: {e}")

            except ValueError as e:
                print(f"Executor Error: {e}")
            except Exception as e:
                print(f"Executor Error: {e}")

        return mcp, working_memory

    def _execute_single_entry(self, tool_instance, mcp: MCP, entry: dict):
        """
        执行单个entry的辅助方法，用于在线程池中调用
        """
        try:
            return tool_instance.execute(mcp, **entry)
        except Exception as e:
            print(
                f"Executor Error in thread: Failed to execute entry for tool '{tool_instance.tool_id}' "
                f"(Instance: {tool_instance.instance_id}): {e}"
            )
            return None


if __name__ == "__main__":
    llm_interface = OpenAIInterface()
    db_interface = RedisClient()
    executor = ToolExecutor(db_interface, LLMFilterSummary(llm_interface, db_interface))
    mcp = MCP(
        session_id="test_session_002",
        user_requirements="预测2030年中国人口",
        executable_command={
            "tools": [
                {
                    "tool": "web_search",
                    "params": {
                        "entries": [
                            {
                                "keywords": ["2030", "中国", "人口", "预测"],
                                "num_results": 3,
                            },
                            {
                                "keywords": ["2025", "中国", "人口"],
                                "num_results": 3,
                            },
                            {
                                "keywords": ["2020", "中国", "人口"],
                                "num_results": 3,
                            },
                        ]
                    },
                }
            ]
        },
    )
    working_memory = WorkingMemory(session_id="test_session_002")
    mcp, working_memory = executor.execute(mcp, working_memory)
    print(f"Executor: WorkingMemory: {working_memory}")
