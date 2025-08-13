# -*- coding: utf-8 -*-
"""
整个工作流的入口，负责接收用户需求并驱动所有 LLM 实体，实现完整的“研究-执行-反思”闭环。
"""
from Data.mcp_models import MCP, WorkingMemory
from Data.strategies import StrategyData
from Interfaces.llm_api_interface import OpenAIInterface
from Interfaces.database_interface import RedisClient
from Entities.strategy_planner import LLMStrategyPlanner
from Entities.task_planner import LLMTaskPlanner
from Entities.filter_summary import LLMFilterSummary
from Entities.verification_entities import PredictionVerification, RequirementsVerification
from Tools.executor import ToolExecutor
import json

class AgentWorkflow:
    """
    整个工作流的入口，负责接收用户需求并驱动所有 LLM 实体。
    """
    def __init__(self, user_requirements: str, session_id: str):
        self.mcp = MCP(user_requirements=user_requirements, session_id=session_id)
        self.working_memory = WorkingMemory()
        self.strategies = StrategyData()

        # 初始化所有接口
        self.llm_interface = OpenAIInterface()
        self.db_interface = RedisClient()  # 实例化 RedisClient


    def run(self):
        """
        启动并执行整个 Agent 工作流，包含完整的闭环和反思机制。
        """
        print(f"--- Starting Agent Workflow for Session ID: {self.mcp.session_id} ---")
        print(f"User Requirements: {self.mcp.user_requirements}")

        # 1. 初始战略规划
        strategy_planner = LLMStrategyPlanner(self.llm_interface)
        self.mcp = strategy_planner.process(self.mcp, self.strategies)
        
        while self.mcp.current_strategy_plan:
            # 2. 任务规划
            task_planner = LLMTaskPlanner(self.llm_interface)
            self.mcp = task_planner.process(self.mcp, self.strategies)
            
            # 3. 命令执行
            if self.mcp.executable_command:
                filter_summary = LLMFilterSummary(self.llm_interface)
                tool_executor = ToolExecutor(db_interface=self.db_interface, llm_summarizer=filter_summary)
                self.working_memory = tool_executor.execute(self.mcp, self.working_memory)
            else:
                print("Warning: No executable command planned. Skipping execution.")
                break

            # 4. 战术反思 (预测验证)
            prediction_verifier = PredictionVerification()
            is_prediction_met = prediction_verifier.verify(self.mcp, self.working_memory)
            
            # 保存当前周期的 MCP 快照
            current_mcp_snapshot = self.mcp.model_dump()
            # 避免历史记录无限嵌套
            current_mcp_snapshot.pop('cycle_history', None) 
            
            # 获取并更新历史记录
            cycle_history = self.mcp.cycle_history
            cycle_history.append(json.dumps(current_mcp_snapshot))
            
            if is_prediction_met:
                print("Prediction met. Proceeding to the next step.")
                # 移除已完成的步骤
                next_strategy_plan = self.mcp.current_strategy_plan[1:]
                # 清空 working_memory 以备下一个循环使用
                self.working_memory.data.clear()
            else:
                print("Prediction not met. Updating execution policy for replanning.")
                failure_feedback = f"The command '{self.mcp.executable_command}' failed to produce data matching schema '{self.mcp.expected_data}'."
                self.strategies.execution_policy.append(failure_feedback)
                # 保持当前战略计划不变，以便重新规划
                next_strategy_plan = self.mcp.current_strategy_plan

            # 创建一个全新的 MCP 实例以实现彻底重置
            self.mcp = MCP(
                session_id=self.mcp.session_id,
                global_cycle_count=self.mcp.global_cycle_count + 1,
                user_requirements=self.mcp.user_requirements,
                current_strategy_plan=next_strategy_plan,
                cycle_history=cycle_history
            )
            print(f"\n--- Starting Global Cycle #{self.mcp.global_cycle_count} ---")

        # 5. 所有战略步骤完成后，进行战略反思 (需求验证)
        requirements_verifier = RequirementsVerification(self.llm_interface)
        is_requirements_met = requirements_verifier.verify(self.mcp)

        if not is_requirements_met:
            print("Overall requirements not met. Updating cognition for strategic replanning.")
            final_failure_feedback = f"The plan execution did not fulfill the user requirement."
            self.strategies.cognition.append(final_failure_feedback)
        else:
            print("--- Agent Workflow Finished Successfully ---")
        
        self.db_interface.disconnect()


if __name__ == '__main__':
    # 模拟从数据库或某个会话管理器获取会话ID
    from Interfaces.database_interface import RedisClient
    db_interface = RedisClient()
    db_interface.connect()
    session_id = db_interface.create_new_session_id()
    db_interface.disconnect()

    USER_REQUEST = "Find the latest news about AI safety research and provide a summary of the top 3 findings."
    workflow = AgentWorkflow(user_requirements=USER_REQUEST, session_id=session_id)
    
    # 实际运行时，请确保所有依赖都已正确实现
    # workflow.run()
    print("AgentWorkflow initialized. Call run() to start the process.")
