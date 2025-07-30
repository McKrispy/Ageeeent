# -*- coding: utf-8 -*-
"""
此文件定义了系统中所有基于 LLM 的核心实体。
这些实体是智能体认知能力的主要承载者，负责规划和摘要等任务。
"""
from abc import ABC, abstractmethod
from Data.mcp_models import MCP
from Interfaces.llm_api_interface import LLMAPIInterface

class BaseLLMEntity(ABC):
    """
    所有 LLM 实体的抽象基类。
    """
    def __init__(self, llm_interface: LLMAPIInterface):
        self.llm_interface = llm_interface

    @abstractmethod
    def process(self, mcp: MCP) -> MCP:
        """
        所有实体都必须实现此方法来处理 MCP 对象。

        Args:
            mcp (MCP): 当前的任务简报。

        Returns:
            MCP: 处理和更新后的任务简报。
        """
        pass

class LLMStrategyPlanner(BaseLLMEntity):
    """
    战略规划器 (What) - 进行高层次战略分解。
    """
    def process(self, mcp: MCP) -> MCP:
        """
        读取用户需求，生成宏观战略计划并更新到 MCP.current_strategy_plan。
        """
        # 1. 构建 Prompt，输入 mcp.user_requirements
        # 2. 调用 self.llm_interface.get_completion
        # 3. 解析结果，更新 mcp.current_strategy_plan
        print("LLMStrategyPlanner: Decomposing user requirements into a high-level strategy.")
        mcp.current_strategy_plan = ["step 1", "step 2", "step 3"]
        return mcp

class LLMTaskPlanner(BaseLLMEntity):
    """
    任务规划器 (How) - 进行精细的战术规划。
    """
    def process(self, mcp: MCP) -> MCP:
        """
        读取宏观步骤，生成具体的子目标和可执行命令，并更新 MCP。
        """
        # 1. 从 mcp.current_strategy_plan 中获取下一步
        # 2. 构建 Prompt，生成子目标、命令和预期数据格式
        # 3. 调用 self.llm_interface.get_completion
        # 4. 解析结果，更新 mcp.current_subgoal, mcp.executable_command, mcp.expected_data_schema
        print("LLMTaskPlanner: Breaking down a strategy step into a specific subgoal and command.")
        mcp.current_subgoal = "Execute search for topic X."
        mcp.executable_command = {"tool": "web_search", "query": "topic X"}
        mcp.expected_data_schema = {"type": "object", "properties": {"summary": {"type": "string"}}}
        return mcp

class LLMFilterSummary(BaseLLMEntity):
    """
    筛选与摘要器 - 将“重型”原始数据转化为轻量级的、高信息密度的摘要。
    """
    def process_data(self, raw_data: Any) -> str:
        """
        处理原始数据，生成摘要。

        Args:
            raw_data (Any): 从工具获取的原始数据。

        Returns:
            str: 数据的摘要。
        """
        # 1. 构建 Prompt，输入原始数据
        # 2. 调用 self.llm_interface.get_completion
        # 3. 返回摘要文本
        print("LLMFilterSummary: Summarizing raw data into a lightweight summary.")
        return "This is a summary of the raw data."
