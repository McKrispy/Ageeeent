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
        读取宏观步骤和短期战术经验，生成具体的子目标和可执行命令，并更新 MCP。
        """
        if not mcp.current_strategy_plan:
            print("Error: No strategy plan to process.")
            return mcp

        print("LLMTaskPlanner: Breaking down a strategy step into a specific subgoal and command.")
        next_step = mcp.current_strategy_plan[0]

        # 将短期战术经验融入 prompt
        policy_prompt = "\n".join(strategies.execution_policy)
        prompt_input = f"Strategic Step: {next_step}\n\nRelevant Tactical Experience:\n{policy_prompt}"
        
        prompt = self.prompt_template.replace('{{strategic_step}}', prompt_input)
        
        # 请求JSON输出格式
        response = self.llm_interface.get_completion(
            prompt, 
            model="gpt-4-turbo", 
            response_format={"type": "json_object"}
        )
        
        try:
            task_json = json.loads(response)
            mcp.current_subgoal = task_json.get("subgoal")
            mcp.executable_command = task_json.get("executable_command")
            mcp.expected_data = task_json.get("expected_data")
            print(f"Generated task: {mcp.current_subgoal}")
            print(f"Executable command: {mcp.executable_command}")
        except json.JSONDecodeError:
            print(f"Error: Failed to decode JSON from LLMTaskPlanner. Response:\n{response}")
            
        return mcp
