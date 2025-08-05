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

class ExecutionLogEntry(BaseModel):
    """
    执行历史中的单个条目，用于归档已完成步骤的摘要和数据指针。
    对应 Reflect 阶段的 Raw Result 的一部分。
    """
    subgoal: str = Field(description="该条目对应的子目标。")
    summary: str = Field(description="执行结果的关键信息摘要。")
    data_pointers: Dict[str, str] = Field(description="指向 RedisJSON 中存储的原始数据的键（指针）集合。")
    status: str = Field(default="Success", description="该步骤的执行状态。")

class MCP(BaseModel):
    """
    MCP (Memory-Context-Prompt) 协议的核心数据类。
    这是一个轻量级的、贯穿任务全程的“任务简报”或“公文包”，以Python对象形式存在。
    它负责传递当前任务的状态、摘要和控制信息，以保持LLM prompt的精简。
    """
    session_id: str = Field(description="标识单次端到端对话的唯一ID。")
    global_cycle_count: int = Field(default=0, description="整个工作流的主循环次数。")
    
    task_id: str = Field(default_factory=lambda: f"task_{uuid.uuid4()}", description="本次复杂任务的全局唯一ID，用作RedisJSON的key前缀。")
    user_requirements: str = Field(description="用户完整的原始需求文本。")
    
    # Plan & Study 阶段的产出
    current_strategy_plan: List[str] = Field(default_factory=list, description="战略规划器输出的宏观步骤列表。")
    current_subgoal: str = Field(default="", description="任务规划器当前正在处理的具体子目标。")
    executable_command: Dict[str, Any] = Field(default_factory=dict, description="由任务规划器生成的、可直接执行的标准化命令。")
    expected_data: Dict[str, Any] = Field(default_factory=dict, description="对当前子目标预期结果的数据规范，用于后续验证。")

    # Execute 阶段的产出
    working_memory: Dict[str, Any] = Field(default_factory=dict, description="一个临时的“便签”，存放当前步骤产生的摘要和数据指针(RedisJSON Keys)。")

    # Reflect 阶段的产出
    execution_history: List[ExecutionLogEntry] = Field(default_factory=list, description="一个包含摘要和指针的日志，记录所有已成功完成的步骤。")

    # 新增：用于追踪所有实体状态的字典
    entity_states: Dict[str, "EntityStatus"] = Field(default_factory=dict, description="存储系统中所有实体（包括LLM实体和工具）的当前状态。")
    
    class Config:
        """Pydantic model configuration."""
        validate_assignment = True

class EntityStatus(BaseModel):
    """
    用于在 MCP 的 entity_states 中记录每个实体状态的模型。
    """
    entity_id: str = Field(description="实体的唯一标识符。")
    name: str = Field(description="实体的友好名称（类名）。")
    cycle_count: int = Field(default=0, description="实体在当前工作流中被执行的轮次计数。")
    status: int = Field(default=0, description="实体的当前状态：0-未开始, 1-正在执行, 2-已完成。")
