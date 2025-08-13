# -*- coding: utf-8 -*-
"""
任务规划器 (How) - 进行精细的战术规划。
"""
import json
from Data.mcp_models import MCP
from Data.strategies import StrategyData
from Entities.base_llm_entity import BaseLLMEntity

class LLMTaskPlanner(BaseLLMEntity):
    """
    任务规划器 (How) - 进行精细的战术规划。
    """
    def process(self, mcp: MCP, strategies: StrategyData) -> MCP:
        """
        读取宏观步骤和短期战术经验，为每个战略计划生成具体的子目标和可执行命令，并更新 MCP。
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
            
            # 请求JSON输出格式
            response = self.llm_interface.get_completion(
                prompt, 
                model="gpt-4-turbo", 
                response_format={"type": "json_object"}
            )
            
            try:
                task_json = json.loads(response)
                
                for sg_data in task_json.get("sub_goals", []):
                    sub_goal = MCP.SubGoal(
                        parent_strategy_plan_id=plan.id,
                        description=sg_data.get("description")
                    )
                    
                    for cmd_data in sg_data.get("executable_commands", []):
                        command = MCP.ExecutableCommand(
                            parent_sub_goal_id=sub_goal.id,
                            tool=cmd_data.get("tool"),
                            params=cmd_data.get("params")
                        )
                        sub_goal.executable_commands.append(command)
                    
                    plan.sub_goals.append(sub_goal)
                    
                print(f"Generated tasks for plan '{plan.description}': {[sg.description for sg in plan.sub_goals]}")

            except json.JSONDecodeError:
                print(f"Error: Failed to decode JSON from LLMTaskPlanner. Response:\n{response}")
                
        return mcp
