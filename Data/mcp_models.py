# -*- coding: utf-8 -*-
"""
此文件定义了项目核心的数据结构，遵循双层记忆系统原则。
主要包括：
1. MCP (Memory-Context-Prompt): 任务全程传递的轻量级“任务简报”对象。
2. 相关的数据模型，用于规范化 MCP 内部的数据，如执行历史记录等。
"""
from typing import List, Dict, Any
from pydantic import BaseModel, Field
import uuid


class WorkingMemory(BaseModel):
    """
    一个独立的数据类，专门用于存放所有在 Execution 阶段获取的外部数据信息。
    它作为一个临时的“便签”，存放当前步骤产生的摘要和数据指针(RedisJSON Keys)。
    """
    data: Dict[str, Any] = Field(default_factory=dict, description="存放当前执行步骤产生的摘要和数据指针(RedisJSON Keys)。")
    '''
    Example of data:
    {
        "test_session_002:0:WebSearchTool:WebSearchTool_57abee32-ff96-495a-9c08-0a34ef7e6bdb": "summary of web search result",
        ...
    }
    '''

    class Config:
        """Pydantic model configuration."""
        validate_assignment = True

class MCP(BaseModel):
    """
    MCP (Memory-Context-Prompt) 协议的核心数据类。
    这是一个轻量级的、贯穿任务全程的“任务简报”或“公文包”，以Python对象形式存在。
    它负责传递当前任务的状态、摘要和控制信息，以保持LLM prompt的精简。
    """
    session_id: str = Field(description="标识单次端到端对话的唯一ID。")
    global_cycle_count: int = Field(default=0, description="整个工作流的主循环次数。")
    
    user_requirements: str = Field(description="用户完整的原始需求文本。")
    
    # Plan & Study 阶段的产出
    current_strategy_plan: List[str] = Field(default_factory=list, description="战略规划器输出的宏观步骤列表。")
    current_subgoal: str = Field(default="", description="任务规划器当前正在处理的具体子目标。")
    executable_command: Dict[str, Any] = Field(default_factory=dict, description="由任务规划器生成的、可直接执行的标准化命令。")
    expected_data: Dict[str, Any] = Field(default_factory=dict, description="对当前子目标预期结果的数据规范，用于后续验证。")

    # 新增：用于存储每个周期结束时 MCP 完整状态的 JSON 字符串列表
    cycle_history: List[str] = Field(default_factory=list, description="存储每个周期结束时 MCP 完整状态的 JSON 字符串列表。")
    
    class Config:
        """Pydantic model configuration."""
        validate_assignment = True
