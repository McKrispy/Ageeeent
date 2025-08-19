# -*- coding: utf-8 -*-
"""
任务规划器 (How) - 进行精细的战术规划。
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
    任务规划器 (How) - 进行精细的战术规划。
    """
    def __init__(self, llm_interface, db_interface=None, entity_id=None):
        super().__init__(llm_interface, db_interface, entity_id)
        self.tool_registry = ToolRegistry()
        self.max_retries = 3

    def process(self, mcp: MCP, strategies: StrategyData) -> MCP:
        """
        批量处理所有战略计划，为每个计划生成子目标和命令，并填充到扁平化的列表中。
        """

        if not mcp.strategy_plans:
            print("Error: No strategy plan to process.")
            return mcp

        print("LLMTaskPlanner: Breaking down strategy plans into specific subgoals and commands.")
        
        # 获取工具注册表信息
        available_tools = self._get_available_tools_info()
        
        # 构建批量处理的prompt
        batch_prompt = self._build_batch_prompt(mcp.strategy_plans, strategies, available_tools)
        
        # 批量调用LLM
        response = self._call_llm_with_retry(batch_prompt)
        
        if response:
            self._process_batch_response(response, mcp)
        else:
            print("Error: Failed to get valid response from LLM after all retries.")
                
        return mcp

    def _get_available_tools_info(self) -> str:
        """
        获取可用工具的信息字符串
        """
        tools = self.tool_registry.list_tools()
        tools_info = []
        
        for tool_name in tools:
            tools_info.append(f"- {tool_name}: 网络搜索和信息获取工具")
        
        return "\n".join(tools_info)
    
    def _format_strategy_plan(self, plan: StrategyPlan) -> str:
        """
        将StrategyPlan的dict格式description转换为字符串
        """
        if isinstance(plan.description, dict):
            # 将dict转换为可读的字符串格式
            formatted_parts = []
            for key, value in plan.description.items():
                formatted_parts.append(f"{key}: {value}")
            return "\n".join(formatted_parts)
        else:
            return str(plan.description)
    
    def _build_batch_prompt(self, strategy_plans: List[StrategyPlan], strategies: StrategyData, tools_info: str) -> str:
        """
        构建批量处理的prompt
        """
        # 将短期战术经验融入 prompt
        policy_prompt = "\n".join(strategies.execution_policy) if strategies.execution_policy else "暂无执行策略经验"
        
        # 格式化所有战略计划
        formatted_plans = []
        for i, plan in enumerate(strategy_plans, 1):
            plan_desc = self._format_strategy_plan(plan)
            formatted_plans.append(f"战略计划{i} (ID: {plan.id}):\n{plan_desc}")
        
        strategic_steps = "\n\n".join(formatted_plans)
        
        # 替换prompt模板中的占位符
        prompt = self.prompt_template.replace('{{strategic_step}}', strategic_steps)
        prompt = prompt.replace('{{execution_policy_info}}', policy_prompt)
        
        # 添加工具信息
        tools_section = f"\n\n**当前可用工具：**\n{tools_info}"
        prompt = prompt + tools_section
        
        return prompt
    
    def _call_llm_with_retry(self, prompt: str) -> str:
        """
        带重试机制的LLM调用
        """
        for attempt in range(self.max_retries):
            try:
                print(f"LLM调用尝试 {attempt + 1}/{self.max_retries}")
                
                response = self.llm_interface.get_completion(
                    prompt,
                    response_format={"type": "json_object"},
                    temperature=0.3,  # 降低随机性，提高一致性
                    max_tokens=4000   # 设置合理的token限制
                )
                
                if response and response.strip():
                    return response
                else:
                    print(f"尝试 {attempt + 1}: 收到空响应")
                    
            except Exception as e:
                print(f"尝试 {attempt + 1} 失败: {e}")
                
            if attempt < self.max_retries - 1:
                wait_time = 2 ** attempt  # 指数退避
                print(f"等待 {wait_time} 秒后重试...")
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
                
                # 每个子目标下应该有对应的可执行命令
                for cmd_data in sg_data.get("executable_commands", []):
                    tool_name = cmd_data.get("tool")
                    
                    # 验证工具是否在注册表中
                    if tool_name in self.tool_registry.list_tools():
                        new_command = ExecutableCommand(
                            parent_sub_goal_id=new_sub_goal.id,
                            tool=tool_name,
                            params=cmd_data.get("params", {})
                        )
                        mcp.executable_commands.append(new_command)
                    else:
                        print(f"Warning: 工具 '{tool_name}' 不在注册表中，跳过此命令")
                
            print(f"批量生成了 {len(mcp.sub_goals)} 个子目标和 {len(mcp.executable_commands)} 个可执行命令")

        except json.JSONDecodeError as e:
            print(f"Error: JSON解析失败: {e}")
            print(f"原始响应: {response[:500]}...")  # 只显示前500字符
        except Exception as e:
            print(f"Error: 处理响应时发生错误: {e}")

if __name__ == "__main__":
    llm_interface = OpenAIInterface()
    llm_task_planner = LLMTaskPlanner(llm_interface)
    db = RedisClient()
    mcp = MCP(session_id="1234567890", user_requirements="How to make a cake", strategy_plans=[StrategyPlan(description={"goal": "Make a cake", "priority": "high"})])
    strategies = StrategyData(execution_policy=["You are a helpful assistant that can help me make a cake."])
    mcp = llm_task_planner.process(mcp, strategies)
    print(mcp.sub_goals)
    print(mcp.executable_commands)
    