# -*- coding: utf-8 -*-
"""
此文件定义了 Executor (执行器) 类。
执行器是连接规划和行动的桥梁，负责调用工具、协调数据流，
并严格遵守"原始数据存入RedisJSON，摘要存入MCP"的核心原则。
"""
import time
import threading
from typing import Dict, Any

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
        self, executable_command, session_id: str, working_memory
    ) -> bool:
        """
        执行单个命令。
        1. 从注册表获取工具类。
        2. 为每个entry创建独立的工具实例。
        3. 并行执行工具。
        4. 工具执行后，将回传的信息包装为规定格式，输出到working_memory中记录。
        5. 返回执行是否成功。
        """
        if not executable_command:
            print("Executor Error: No executable command provided.")
            return False

        # 将ExecutableCommand转换为执行器期望的格式
        if hasattr(executable_command, 'tool') and hasattr(executable_command, 'params'):
            # 这是一个ExecutableCommand对象
            tool_name = executable_command.tool
            tool_params = executable_command.params
        else:
            # 这是旧格式的字典
            tools = executable_command.get("tools")
            if not tools:
                print("Executor Error: No tools found in command.")
                return False
            # 假设只有一个工具
            tool_data = tools[0]
            tool_name = tool_data.get("tool")
            tool_params = tool_data.get("params", {})

        print(f"Executor: Executing tool '{tool_name}' with params: {tool_params}")

        try:
            # 1. 从注册表获取工具类
            tool_class = self.tool_registry.get_tool_class(tool_name)
            
            # 2. 获取所有entries
            entries = tool_params.get("entries", [])
            if not entries:
                print(f"Executor: No entries found for tool '{tool_name}'")
                return False

            # 3. 并行执行每个entry，为每个entry创建独立的tool_instance
            execution_success = True
            
            with ThreadPoolExecutor(max_workers=min(len(entries), 10)) as executor_pool:
                # 提交所有任务
                future_to_entry = {}
                for entry in entries:
                    time.sleep(0.2)
                    # 为每个entry创建独立的tool_instance
                    tool_instance = tool_class(
                        db_interface=self.db_interface, 
                        llm_summarizer=self.llm_summarizer
                    )
                    
                    # 创建MCP对象用于工具执行
                    temp_mcp = type('MCP', (), {'session_id': session_id})()
                    
                    # 提交任务到线程池
                    future = executor_pool.submit(
                        self._execute_single_entry,
                        tool_instance,
                        temp_mcp,
                        entry
                    )
                    future_to_entry[future] = (tool_instance, entry)

                for future in as_completed(future_to_entry):
                    tool_instance, entry = future_to_entry[future]
                    try:
                        execution_result = future.result()
                        if execution_result and isinstance(execution_result, dict):
                            with threading.Lock():
                                # 8.3: 将工具实例回传的信息，包装为规定格式，输出到working_memory中记录
                                for redis_key, raw_data in execution_result.items():
                                    working_memory.data[redis_key] = raw_data
                                    print(f"Executor: Stored result in working_memory with key: {redis_key}")
                        else:
                            print(f"Executor Warning: No valid result from tool instance {tool_instance.entity_id}")
                    except Exception as e:
                        print(f"Executor Error: {e}")
                        execution_success = False

            return execution_success

        except ValueError as e:
            print(f"Executor Error: {e}")
            return False
        except Exception as e:
            print(f"Executor Error: {e}")
            return False

    def _execute_single_entry(self, tool_instance, mcp, entry: dict):
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
    from Data.mcp_models import ExecutableCommand, WorkingMemory
    
    llm_interface = OpenAIInterface()
    db_interface = RedisClient()
    executor = ToolExecutor(db_interface, LLMFilterSummary(llm_interface))
    
    # 创建ExecutableCommand对象测试
    command = ExecutableCommand(
        parent_sub_goal_id="test_sg_001",
        tool="web_search",
        params={
            "entries": [
                {
                    "keywords": ["2030", "中国", "人口", "预测"],
                    "num_results": 3,
                },
                {
                    "keywords": ["2025", "中国", "人口"],
                    "num_results": 3,
                },
            ]
        }
    )
    
    session_id = "test_session_002"
    working_memory = WorkingMemory()
    
    success = executor.execute(command, session_id, working_memory)
    print(f"Executor: Execution success: {success}")
    print(f"Executor: Working memory data: {working_memory.data}")
