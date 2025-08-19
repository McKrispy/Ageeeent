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
            strategy_plans = json.loads(response).get("strategy_plans", [])
            mcp.strategy_plans = [StrategyPlan(description=plan) for plan in strategy_plans]
            
            print(f"Generated strategy plans: {[plan for plan in mcp.strategy_plans]}")
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
