# -*- coding: utf-8 -*-
"""
此文件定义了 Executor (执行器) 类。
执行器是连接规划和行动的桥梁，负责调用工具、协调数据流，
并严格遵守“原始数据存入RedisJSON，摘要存入MCP”的核心原则。
执行器类，负责调用工具并协调与数据库的交互。
"""
from Data.mcp_models import MCP
from Interfaces.database_interface import DatabaseInterface
from Entities.llm_entities import LLMFilterSummary
from .tool_registry import ToolRegistry
import hashlib
import json

class ToolExecutor:
    """
    执行器类，执行MCP中指定的命令。
    """
    def __init__(self, db_interface: DatabaseInterface, summarizer: LLMFilterSummary):
        """
        初始化执行器。

        Args:
            db_interface (DatabaseInterface): 数据库接口的实例，用于与 RedisJSON 交互。
            summarizer (LLMFilterSummary): LLM 摘要器的实例，用于处理原始数据。
        """
        self.db_interface = db_interface
        self.summarizer = summarizer
        self.tool_registry = ToolRegistry()

    def execute_command(self, mcp: MCP) -> MCP:
        """
        执行 MCP 中定义的命令。

        Args:
            mcp (MCP): 包含待执行命令的任务简报。

        Returns:
            MCP: 更新了执行结果（摘要和指针）的任务简报。
        """
        command = mcp.executable_command
        tool_name = command.get("tool")
        tool_params = command.get("params", {})

        if not tool_name:
            raise ValueError("No tool specified in the executable command.")

        # 1. 从工具注册表中获取工具并执行
        tool = self.tool_registry.get_tool(tool_name)
        print(f"Executor: Executing tool '{tool_name}' with params: {tool_params}")
        raw_data = tool.execute(**tool_params)

        # 2. 将原始数据存入 RedisJSON
        #    Key 的格式: task_id:data_type:unique_hash
        data_key = f"{mcp.task_id}:{tool_name}:{hash(str(raw_data))}"
        self.db_interface.store_data(data_key, raw_data)
        print(f"Executor: Stored raw data in database with key '{data_key}'.")

        # 3. 调用 LLMFilterSummary 生成摘要
        summary = self.summarizer.process_data(raw_data)
        print("Executor: Generated summary for the raw data.")

        # 4. 更新 MCP 的 working_memory
        mcp.working_memory = {
            "summary": summary,
            "data_pointer": data_key
        }
        print("Executor: Updated MCP's working memory with summary and data pointer.")

        return mcp
