# -*- coding: utf-8 -*-
"""
Task Planner (How) - Performs detailed tactical planning.
"""
import json
import time
from typing import Dict, List, Any
from Data.mcp_models import MCP, SubGoal, ExecutableCommand, StrategyPlan
from Data.strategies import StrategyData
from Entities.base_llm_entity import BaseLLMEntity
from Interfaces.llm_api_interface import OpenAIInterface
from Interfaces.database_interface import RedisClient
from Tools.tool_registry import ToolRegistry

class LLMTaskPlanner(BaseLLMEntity):
    """
    Task Planner (How) - Performs detailed tactical planning.
    """
    def __init__(self, llm_interface, db_interface=None, entity_id=None):
        super().__init__(llm_interface, db_interface, entity_id)
        self.tool_registry = ToolRegistry()
        self.max_retries = 3

    def process(self, mcp: MCP, strategies: StrategyData) -> MCP:
        """
        Batch process all strategy plans, generate subgoals and commands for each plan, and populate into flattened lists.
        """

        if not mcp.strategy_plans:
            print("Error: No strategy plan to process.")
            return mcp

        print("LLMTaskPlanner: Breaking down strategy plans into specific subgoals and commands.")
        
        # Get tool registry information
        available_tools = self._get_available_tools_info()
        
        # Build batch processing prompt
        batch_prompt = self._build_batch_prompt(mcp.strategy_plans, strategies, available_tools)
        
        # Batch call LLM
        response = self._call_llm_with_retry(batch_prompt)
        
        if response:
            self._process_batch_response(response, mcp)
        else:
            print("Error: Failed to get valid response from LLM after all retries.")
                
        return mcp

    def _get_available_tools_info(self) -> str:
        """
        Get information string for available tools
        """
        tools = self.tool_registry.list_tools()
        tools_info = []
        
        for tool_name in tools:
            tools_info.append(f"- {tool_name}: Web search and information retrieval tool")
        
        return "\n".join(tools_info)
    
    def _format_strategy_plan(self, plan: StrategyPlan) -> str:
        """
        Convert StrategyPlan's dict format description to string
        """
        if isinstance(plan.description, dict):
            # Convert dict to readable string format
            formatted_parts = []
            for key, value in plan.description.items():
                formatted_parts.append(f"{key}: {value}")
            return "\n".join(formatted_parts)
        else:
            return str(plan.description)
    
    def _build_batch_prompt(self, strategy_plans: List[StrategyPlan], strategies: StrategyData, tools_info: str) -> str:
        """
        Build batch processing prompt
        """
        # Integrate short-term tactical experience into prompt
        policy_prompt = "\n".join(strategies.execution_policy) if strategies.execution_policy else "No execution policy experience"
        
        # 格式化所有战略计划
        formatted_plans = []
        for i, plan in enumerate(strategy_plans, 1):
            plan_desc = self._format_strategy_plan(plan)
            formatted_plans.append(f"Strategy plan{i} (ID: {plan.id}):\n{plan_desc}")
        
        strategic_steps = "\n\n".join(formatted_plans)
        
        # Replace placeholder in prompt template
        prompt = self.prompt_template.replace('{{strategic_step}}', strategic_steps)
        prompt = prompt.replace('{{execution_policy_info}}', policy_prompt)
        
        # Add tool information
        tools_section = f"\n\n**Current available tools:**\n{tools_info}"
        prompt = prompt + tools_section
        
        return prompt
    
    def _call_llm_with_retry(self, prompt: str) -> str:
        """
        LLM call with retry mechanism
        """
        for attempt in range(self.max_retries):
            try:
                print(f"LLM call attempt {attempt + 1}/{self.max_retries}")
                
                response = self.llm_interface.get_completion(
                    prompt,
                    response_format={"type": "json_object"},
                    temperature=0.3,
                    max_tokens=4000 
                )
                
                if response and response.strip():
                    return response
                else:
                    print(f"Attempt {attempt + 1}: Received empty response")
                    
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                
            if attempt < self.max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Waiting {wait_time} seconds before retrying...")
                time.sleep(wait_time)
        
        return None
    
    def _process_batch_response(self, response: str, mcp: MCP) -> None:
        """
        处理批量LLM响应
        """
        try:
            task_json = json.loads(response)
            
            # 处理批量响应中的子目标
            for sg_data in task_json.get("sub_goals", []):
                # 查找对应的strategy_plan_id
                parent_plan_id = sg_data.get("parent_strategy_plan_id")
                
                # 如果没有指定parent_id，使用第一个可用的plan
                if not parent_plan_id and mcp.strategy_plans:
                    parent_plan_id = mcp.strategy_plans[0].id
                
                new_sub_goal = SubGoal(
                    parent_strategy_plan_id=parent_plan_id,
                    description=sg_data.get("description", "")
                )
                mcp.sub_goals.append(new_sub_goal)
                
                for cmd_data in sg_data.get("executable_commands", []):
                    tool_name = cmd_data.get("tool")
                    
                    if tool_name in self.tool_registry.list_tools():
                        new_command = ExecutableCommand(
                            parent_sub_goal_id=new_sub_goal.id,
                            tool=tool_name,
                            params=cmd_data.get("params", {})
                        )
                        mcp.executable_commands.append(new_command)
                    else:
                        print(f"Warning:'{tool_name}' is not in the registry, skipping this command")
                
            print(f"Batch generated {len(mcp.sub_goals)} subgoals and {len(mcp.executable_commands)} executable commands")

        except json.JSONDecodeError as e:
            print(f"Error: JSON parsing failed: {e}")
            print(f"Original response: {response[:500]}...") 
        except Exception as e:
            print(f"Error: Error processing response: {e}")

if __name__ == "__main__":
    llm_interface = OpenAIInterface()
    llm_task_planner = LLMTaskPlanner(llm_interface)
    db = RedisClient()
    mcp = MCP(session_id="1234567890", user_requirements="How to make a cake", strategy_plans=[StrategyPlan(description={"goal": "Make a cake", "priority": "high"})])
    strategies = StrategyData(execution_policy=["You are a helpful assistant that can help me make a cake."])
    mcp = llm_task_planner.process(mcp, strategies)
    print(mcp.sub_goals)
    print(mcp.executable_commands)
    