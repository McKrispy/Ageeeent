# -*- coding: utf-8 -*-
"""
This file defines the core data structures of the project, following the dual-layer memory system principle.
Mainly includes:
1. MCP (Memory-Context-Prompt): Lightweight "task brief" object passed throughout the task.
2. Related data models for standardizing data within MCP, such as execution history records.
"""
from typing import List, Dict, Any
from pydantic import BaseModel, Field
import uuid

class CompletionRequirement(BaseModel):
    original_input: str = Field(description="User's original input.")
    supplementary_content: str = Field(description="Content supplemented by user based on questions.")
    profile_analysis: str = Field(description="User profile analyzed from the previous two.")

class StrategyPlan(BaseModel):
    id: str = Field(default_factory=lambda: f"sp_{uuid.uuid4()}", description="Unique ID of the strategy plan.")
    description: dict[str, Any] = Field(description="Description of the strategy plan.")
    is_completed: bool = Field(default=False, description="Mark whether this strategy plan is completed.")

class SubGoal(BaseModel):
    id: str = Field(default_factory=lambda: f"sg_{uuid.uuid4()}", description="Unique ID of the subgoal.")
    parent_strategy_plan_id: str = Field(description="ID of the parent strategy plan.")
    description: str = Field(description="Description of the subgoal.")
    is_completed: bool = Field(default=False, description="Mark whether this subgoal is completed.")

class ExecutableCommand(BaseModel):
    id: str = Field(default_factory=lambda: f"ec_{uuid.uuid4()}", description="Unique ID of the executable command.")
    parent_sub_goal_id: str = Field(description="ID of the parent subgoal.")
    tool: str = Field(description="Name of the tool to use.")
    params: Dict[str, Any] = Field(default_factory=dict, description="Parameters of the tool.")
    is_completed: bool = Field(default=False, description="Mark whether this command has been executed.")


class WorkingMemory(BaseModel):
    """
    A separate data class, specifically for storing all external data information obtained in the Execution stage.
    It is a temporary "note", storing the summary and data pointers (RedisJSON Keys) produced by the current step.
    """
    data: Dict[str, Any] = Field(default_factory=dict, description="Summary and data pointers (RedisJSON Keys) produced by the current execution step.")
    """
    Example of data:
    {
        "test_session_002:0:WebSearchTool:WebSearchTool_57abee32-ff96-495a-9c08-0a34ef7e6bdb": "summary of web search result",
        ...
    }
    """

    class Config:
        """Pydantic model configuration."""
        validate_assignment = True

class MCP(BaseModel):
    """
    MCP (Memory-Context-Prompt) core data class.
    This is a lightweight, throughout the task "task brief" or "portfolio", in the form of a Python object.
    It is responsible for passing the current task status, summary, and control information to keep the LLM prompt concise.
    """
    session_id: str = Field(description="Unique ID of the session.")
    global_cycle_count: int = Field(default=0, description="Main loop count of the workflow.")
    
    user_requirements: str = Field(description="User's complete original requirements text.")
    completion_requirement: CompletionRequirement = Field(default=None, description="Complete user requirements after processing and analysis.")
    
    strategy_plans: List[StrategyPlan] = Field(default_factory=list, description="Flat list of all strategy plans.")
    sub_goals: List[SubGoal] = Field(default_factory=list, description="Flat list of all subgoals.")
    executable_commands: List[ExecutableCommand] = Field(default_factory=list, description="Flat list of all executable commands.")
    
    class Config:
        """Pydantic model configuration."""
        validate_assignment = True
