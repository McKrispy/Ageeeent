# -*- coding: utf-8 -*-
"""
此文件定义了 Executor (执行器) 类。
执行器是连接规划和行动的桥梁，负责调用工具、协调数据流，
并严格遵守"原始数据存入RedisJSON，摘要存入MCP"的核心原则。
"""
from Data.mcp_models import MCP, WorkingMemory, ExecutableCommand
from Interfaces.database_interface import RedisClient
from Interfaces.llm_api_interface import OpenAIInterface, GoogleCloudInterface
from Entities.filter_summary import LLMFilterSummary
from .tool_registry import ToolRegistry

from queue import Queue
import threading

class ToolExecutor:
    def __init__(self, db_interface: RedisClient, llm_summarizer: LLMFilterSummary):
        self.db_interface = db_interface
        self.llm_summarizer = llm_summarizer
        self.tool_registry = ToolRegistry()
        self.entity_id = self.__class__.__name__
        
        self._active_threads = 0
        self._thread_lock = threading.Lock()
        self._result_queue = Queue()
    
    def execute(self, mcp: MCP, working_memory: WorkingMemory) -> bool:
        executable_commands = mcp.executable_commands
        
        if not executable_commands:
            return False
        
        batch_size = len(executable_commands)
        results = {}
        
        for i in range(0, len(executable_commands), batch_size):
            batch = executable_commands[i:i + batch_size]
            
            batch_results = self._execute_batch(mcp, batch)
            results.update(batch_results)
            
            if hasattr(mcp, 'should_stop') and mcp.should_stop:
                break
        
        working_memory.data.update(results)
        return True
    
    def _execute_batch(self, mcp: MCP, commands):
        """执行一批命令"""
        threads = []
        results = {}
        results_lock = threading.Lock()
        
        for cmd in commands:
            thread = threading.Thread(
                target=self._execute_single_cmd_threaded,
                args=(mcp, cmd, results, results_lock)
            )
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        return results
    
    def _execute_single_cmd_threaded(self, mcp: MCP, cmd, results, results_lock):
        """在线程中执行单个命令"""
        try:
            tool_class = self.tool_registry.get_tool_class(cmd.tool)
            tool_instance = tool_class(self.db_interface, self.llm_summarizer)
            
            result = tool_instance.execute(mcp, executable_command=cmd)
            if result:
                with results_lock:
                    results[cmd.id] = result
                
        except Exception as e:
            print(f"Thread execution error: {e}")


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
