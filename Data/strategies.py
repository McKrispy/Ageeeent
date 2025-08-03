# -*- coding: utf-8 -*-
"""
此文件定义了用于存储和管理智能体长期与短期策略的数据类。
这些策略会在反思阶段根据任务执行的成败进行动态更新，
从而指导未来规划，实现智能体的自我学习和进化。
"""
from typing import List
from pydantic import BaseModel, Field

class StrategyData(BaseModel):
    """
    一个用于存储智能体认知和执行策略的数据容器。
    这个对象旨在被持久化，并在不同任务之间共享，以实现经验积累。
    """

    cognition: List[str] = Field(
        default_factory=list,
        description="长期战略记忆。用于指导 LLM Strategy Planner (战略规划器) 进行更高层次的规划。在战略反思（Requirements Verification 失败）后更新。"
    )

    execution_policy: List[str] = Field(
        default_factory=list,
        description="短期战术经验。用于指导 LLM Task Planner (任务规划器) 进行更精确的战术规划。在战术修正（Prediction Verification 失败）后更新。"
    )

    class Config:
        """Pydantic model configuration."""
        validate_assignment = True
