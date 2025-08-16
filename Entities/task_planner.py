# -*- coding: utf-8 -*-
"""
任务规划器 (How) - 进行精细的战术规划。
"""
import json
from Data.mcp_models import MCP, SubGoal, ExecutableCommand, StrategyPlan
from Data.strategies import StrategyData
from Entities.base_llm_entity import BaseLLMEntity
from Interfaces.llm_api_interface import OpenAIInterface
from Interfaces.database_interface import RedisClient

class LLMTaskPlanner(BaseLLMEntity):
    """
    任务规划器 (How) - 进行精细的战术规划。
    """
    def process(self, mcp: MCP, strategies: StrategyData) -> MCP:
        """
        遍历所有战略计划，为每个计划生成子目标和命令，并填充到扁平化的列表中。
        """

        if not mcp.strategy_plans:
            print("Error: No strategy plan to process.")
            return mcp

        print("LLMTaskPlanner: Breaking down strategy plans into specific subgoals and commands.")
        
        for plan in mcp.strategy_plans:
            # 将短期战术经验融入 prompt
            policy_prompt = "\n".join(strategies.execution_policy)
            prompt_input = f"Strategic Step: {plan.description}\n\nRelevant Tactical Experience:\n{policy_prompt}"
            
            prompt = self.prompt_template.replace('{{strategic_step}}', prompt_input)
            
            response = self.llm_interface.get_completion(
                prompt, 
                response_format={"type": "json_object"}
            )
            
            try:
                task_json = json.loads(response)
                
                # LLM应该返回一个包含子目标列表的JSON
                for sg_data in task_json.get("sub_goals", []):
                    new_sub_goal = SubGoal(
                        parent_strategy_plan_id=plan.id,
                        description=sg_data.get("description")
                    )
                    mcp.sub_goals.append(new_sub_goal)
                    
                    # 每个子目标下应该有对应的可执行命令
                    for cmd_data in sg_data.get("executable_commands", []):
                        new_command = ExecutableCommand(
                            parent_sub_goal_id=new_sub_goal.id,
                            tool=cmd_data.get("tool"),
                            params=cmd_data.get("params", {})
                        )
                        mcp.executable_commands.append(new_command)
                    
                print(f"Generated tasks for plan '{plan.description}'")

            except json.JSONDecodeError:
                print(f"Error: Failed to decode JSON from LLMTaskPlanner. Response:\n{response}")
                
        return mcp

if __name__ == "__main__":
    llm_interface = OpenAIInterface()
    llm_task_planner = LLMTaskPlanner(llm_interface)
    db = RedisClient()
    mcp = MCP(session_id="1234567890", user_requirements="How to make a cake", strategy_plans=[StrategyPlan(description="Make a cake")])
    strategies = StrategyData(execution_policy=["You are a helpful assistant that can help me make a cake."])
    mcp = llm_task_planner.process(mcp, strategies)
    print(mcp.sub_goals)
    print(mcp.executable_commands)
    