# -*- coding: utf-8 -*-
"""
此文件定义了项目核心的数据结构，遵循双层记忆系统原则。
主要包括：
1. MCP (Memory-Context-Prompt): 任务全程传递的轻量级“任务简报”对象。
2. 相关的数据模型，用于规范化 MCP 内部的数据，如执行历史记录等。
"""
from typing import List, Dict, Any, ForwardRef
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

    class ExecutableCommand(BaseModel):
        id: str = Field(default_factory=lambda: f"ec_{uuid.uuid4()}", description="可执行命令的唯一ID。")
        parent_sub_goal_id: str = Field(description="父子目标的ID。")
        tool: str = Field(description="要使用的工具名称。")
        params: Dict[str, Any] = Field(description="工具的参数。")

    class SubGoal(BaseModel):
        id: str = Field(default_factory=lambda: f"sg_{uuid.uuid4()}", description="子目标的唯一ID。")
        parent_strategy_plan_id: str = Field(description="父战略计划的ID。")
        description: str = Field(description="子目标的描述。")
        executable_commands: List['MCP.ExecutableCommand'] = Field(default_factory=list, description="与此子目标关联的可执行命令列表。")

    class StrategyPlan(BaseModel):
        id: str = Field(default_factory=lambda: f"sp_{uuid.uuid4()}", description="战略计划的唯一ID。")
        description: str = Field(description="战略计划的描述。")
        sub_goals: List['MCP.SubGoal'] = Field(default_factory=list, description="与此战略计划关联的子目标列表。")

    session_id: str = Field(description="标识单次端到端对话的唯一ID。")
    global_cycle_count: int = Field(default=0, description="整个工作流的主循环次数。")
    
    user_requirements: str = Field(description="用户完整的原始需求文本。")
    
    # Plan & Study 阶段的产出
    strategy_plans: List[StrategyPlan] = Field(default_factory=list, description="战略规划器输出的宏观步骤列表。")

    # 新增：用于存储每个周期结束时 MCP 完整状态的 JSON 字符串列表
    cycle_history: List[str] = Field(default_factory=list, description="存储每个周期结束时 MCP 完整状态的 JSON 字符串列表。")
    
    class Config:
        """Pydantic model configuration."""
        validate_assignment = True

# Pydantic v2 a little bit different for ForwardRef
MCP.SubGoal.model_rebuild()
MCP.StrategyPlan.model_rebuild()
