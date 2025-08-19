# -*- coding: utf-8 -*-
"""
战略规划器 (What) - 进行高层次战略分解。
"""
from Data.mcp_models import MCP, StrategyPlan
from Data.strategies import StrategyData
from Entities.base_llm_entity import BaseLLMEntity
from Interfaces.llm_api_interface import OpenAIInterface
from Interfaces.database_interface import RedisClient
import json

class LLMStrategyPlanner(BaseLLMEntity):
    """
    战略规划器 (What) - 进行高层次战略分解。
    """
    def process(self, mcp: MCP, strategies: StrategyData) -> MCP:
        """
        读取用户需求和长期战略记忆，生成宏观战略计划并更新到 MCP.strategy_plans。
        """

        print("LLMStrategyPlanner: Decomposing user requirements into a high-level strategy.")
        
        # 将长期战略记忆融入 prompt
        cognition_prompt = "\n".join(strategies.cognition)
        prompt_input = f"User Request: {mcp.user_requirements}\n\nRelevant Strategic Memories:\n{cognition_prompt}"

        prompt = self.prompt_template.replace('{{user_requirements}}', prompt_input)
        
        response = self.llm_interface.get_completion(prompt, response_format={"type": "json_object"})
        if response:
            response_data = json.loads(response)
            task_type = response_data.get("task_type", "未知任务类型")
            task_complexity = response_data.get("task_complexity", "中等")
            strategy_plans = response_data.get("strategy_plans", [])
            
            print(f"Identified task type: {task_type}, complexity: {task_complexity}")
            
            # 处理新的strategy_plans格式
            for plan in strategy_plans:
                if isinstance(plan, dict):
                    # 新格式：包含objective, scope, priority, rationale
                    plan_dict = {
                        "task_type": task_type,
                        "task_complexity": task_complexity,
                        "objective": plan.get("objective", ""),
                        "scope": plan.get("scope", ""),
                        "priority": plan.get("priority", "中"),
                        "rationale": plan.get("rationale", ""),
                        "type": "strategic_plan"
                    }
                elif isinstance(plan, str):
                    # 如果是字符串，转换为dict格式
                    plan_dict = {
                        "task_type": task_type,
                        "task_complexity": task_complexity,
                        "description": plan, 
                        "type": "strategic_plan"
                    }
                else:
                    # 其他情况，转换为字符串再包装为dict
                    plan_dict = {
                        "task_type": task_type,
                        "task_complexity": task_complexity,
                        "description": str(plan), 
                        "type": "strategic_plan"
                    }
                
                mcp.strategy_plans.append(StrategyPlan(description=plan_dict))
            
            print(f"Generated {len(mcp.strategy_plans)} strategy plans for {task_type} task")
        else:
            print("Error: LLMStrategyPlanner received no response.")
        
        return mcp

if __name__ == "__main__":
    llm_interface = OpenAIInterface()
    llm_strategy_planner = LLMStrategyPlanner(llm_interface)
    db = RedisClient()
    mcp = MCP(session_id="1234567890", user_requirements="How to make a cake", strategy_plans=[])
    strategies = StrategyData(execution_policy=["You are a helpful assistant that can help me make a cake."])
    mcp = llm_strategy_planner.process(mcp, strategies)
    print(mcp.strategy_plans)
