# -*- coding: utf-8 -*-
"""
整个工作流的入口，负责接收用户需求并驱动所有 LLM 实体，实现完整的“研究-执行-反思”闭环。
"""
from Data.mcp_models import MCP
from Data.strategies import StrategyData
from Interfaces.llm_api_interface import OpenAIInterface
from Interfaces.database_interface import RedisJSONInterface
from Entities.strategy_planner import LLMStrategyPlanner
from Entities.task_planner import LLMTaskPlanner
from Entities.filter_summary import LLMFilterSummary
from Entities.verification_entities import PredictionVerification, RequirementsVerification
from Tools.executor import ToolExecutor

class AgentWorkflow:
    """
    整个工作流的入口，负责接收用户需求并驱动所有 LLM 实体。
    """
    def __init__(self, user_requirements: str):
        self.mcp = MCP(user_requirements=user_requirements)
        self.strategies = StrategyData()  # 加载或初始化策略

        # 初始化所有接口和工具
        self.llm_interface = OpenAIInterface()
        self.db_interface = RedisJSONInterface()
        self.tool_executor = ToolExecutor(db_interface=self.db_interface, llm_summarizer=None)
        
        # 初始化所有 LLM 实体
        self.strategy_planner = LLMStrategyPlanner(self.llm_interface)
        self.task_planner = LLMTaskPlanner(self.llm_interface)
        
        # 初始化验证实体
        self.prediction_verifier = PredictionVerification()
        self.requirements_verifier = RequirementsVerification(self.llm_interface) # 需求验证需要LLM

    def run(self):
        """
        启动并执行整个 Agent 工作流，包含完整的闭环和反思机制。
        """
        print(f"--- Starting Agent Workflow for: {self.mcp.user_requirements} ---")
        self.db_interface.connect()

        # 1. 初始战略规划
        self.mcp = self.strategy_planner.process(self.mcp, self.strategies)
        
        while self.mcp.current_strategy_plan:
            # 2. 任务规划
            self.mcp = self.task_planner.process(self.mcp, self.strategies)
            
            # 3. 命令执行
            if self.mcp.executable_command:
                self.mcp = self.tool_executor.execute(self.mcp)
            else:
                print("Warning: No executable command planned. Skipping execution.")
                # 可能需要一个错误处理或重规划的逻辑
                break

            # 4. 战术反思 (预测验证)
            is_prediction_met = self.prediction_verifier.verify(self.mcp)
            
            if is_prediction_met:
                print("Prediction met. Archiving results and proceeding.")
                # 归档成功步骤的结果
                self.mcp.execution_history.append(self.mcp.working_memory)
                self.mcp.working_memory = {} # 清空工作内存
                self.mcp.current_strategy_plan.pop(0) # 移除已完成的步骤
            else:
                print("Prediction not met. Updating execution policy for replanning.")
                # 更新短期战术经验
                failure_feedback = f"The command '{self.mcp.executable_command}' failed to produce data matching schema '{self.mcp.expected_data}'."
                self.strategies.execution_policy.append(failure_feedback)
                # 无需移除步骤，循环将自动使用更新后的策略重新规划当前步骤
        
        # 5. 所有战略步骤完成后，进行战略反思 (需求验证)
        is_requirements_met = self.requirements_verifier.verify(self.mcp)

        if not is_requirements_met:
            print("Overall requirements not met. Updating cognition for strategic replanning.")
            # 更新长期战略记忆
            final_failure_feedback = f"The plan '{self.mcp.execution_history}' did not fulfill the user requirement: '{self.mcp.user_requirements}'"
            self.strategies.cognition.append(final_failure_feedback)
            # (可选) 可以选择重新启动整个 run 循环进行战略重规划
            # self.run() 
        else:
            print("--- Agent Workflow Finished Successfully ---")
        
        self.db_interface.disconnect()


if __name__ == '__main__':
    USER_REQUEST = "Find the latest news about AI safety research and provide a summary of the top 3 findings."
    workflow = AgentWorkflow(user_requirements=USER_REQUEST)
    # 你需要一个`Tools/executor.py`的有效实现，以及修改`verification_entities.py`来提供真实的验证逻辑
    # workflow.run() 
    print("AgentWorkflow initialized. Call run() to start the process (requires implemented tools and verifiers).")
