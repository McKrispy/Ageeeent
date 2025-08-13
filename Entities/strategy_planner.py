# -*- coding: utf-8 -*-
"""
战略规划器 (What) - 进行高层次战略分解。
"""
from Data.mcp_models import MCP
from Data.strategies import StrategyData
from Entities.base_llm_entity import BaseLLMEntity

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
        
        response = self.llm_interface.get_completion(prompt, model="gpt-4")
        
        if response:
            plan_descriptions = [line.split('.', 1)[-1].strip() for line in response.strip().split('\n') if line.strip()]
            
            mcp.strategy_plans = [MCP.StrategyPlan(description=desc) for desc in plan_descriptions]
            
            print(f"Generated strategy plans: {[plan.description for plan in mcp.strategy_plans]}")
        else:
            print("Error: LLMStrategyPlanner received no response.")
        
        return mcp
