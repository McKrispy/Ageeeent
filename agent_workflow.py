# -*- coding: utf-8 -*-
"""
整个工作流的入口，负责接收用户需求并驱动所有 LLM 实体，实现完整的“研究-执行-反思”闭环。
"""
from Data.mcp_models import MCP
from Data.strategies import StrategyData
from Interfaces.llm_api_interface import OpenAIInterface
from Interfaces.database_interface import RedisClient  # 更改导入
from Entities.strategy_planner import LLMStrategyPlanner
from Entities.task_planner import LLMTaskPlanner
from Entities.filter_summary import LLMFilterSummary
from Entities.verification_entities import PredictionVerification, RequirementsVerification
from Tools.executor import ToolExecutor

class AgentWorkflow:
    """
    整个工作流的入口，负责接收用户需求并驱动所有 LLM 实体。
    """
    def __init__(self, user_requirements: str, session_id: str):
        self.mcp = MCP(user_requirements=user_requirements, session_id=session_id)
        self.strategies = StrategyData()

        # 初始化所有接口和工具
        self.llm_interface = OpenAIInterface()
        self.db_interface = RedisClient()  # 实例化 RedisClient
        
        # 初始化所有 LLM 实体
        self.strategy_planner = LLMStrategyPlanner(self.llm_interface)
        self.task_planner = LLMTaskPlanner(self.llm_interface)
        self.filter_summary = LLMFilterSummary(self.llm_interface)
        
        # 将 db_interface 传递给 ToolExecutor
        self.tool_executor = ToolExecutor(db_interface=self.db_interface, llm_summarizer=self.filter_summary)
        
        # 初始化验证实体
        self.prediction_verifier = PredictionVerification()
        self.requirements_verifier = RequirementsVerification(self.llm_interface)

        # 注册所有实体以进行状态追踪
        self._register_entities()

    def _register_entities(self):
        """
        将工作流中的所有实体注册到MCP中，以便追踪状态。
        """
        entities = [
            self.strategy_planner, self.task_planner, self.filter_summary,
            self.tool_executor, self.prediction_verifier, self.requirements_verifier
        ]
        for entity in entities:
            # 确保实体有 entity_id 属性
            if not hasattr(entity, 'entity_id'):
                entity.entity_id = entity.__class__.__name__
                
            self.mcp.entity_states[entity.entity_id] = {
                "name": entity.__class__.__name__,
                "cycle_count": 0,
                "status": 0
            }
        print("All entities registered in MCP.")

    def _reset_entity_statuses(self):
        """
        在一个新的大循环开始前，重置所有实体的状态为“未开始”。
        """
        for entity_id in self.mcp.entity_states:
            self.mcp.entity_states[entity_id]['status'] = 0
        print("--- All entity statuses reset for new cycle. ---")

    def run(self):
        """
        启动并执行整个 Agent 工作流，包含完整的闭环和反思机制。
        """
        print(f"--- Starting Agent Workflow for Session ID: {self.mcp.session_id} ---")
        print(f"User Requirements: {self.mcp.user_requirements}")
        self.db_interface.connect()

        # 1. 初始战略规划
        self.mcp = self.strategy_planner.process(self.mcp, self.strategies)
        
        while self.mcp.current_strategy_plan:
            self.mcp.global_cycle_count += 1
            print(f"\n--- Starting Global Cycle #{self.mcp.global_cycle_count} ---")
            self._reset_entity_statuses()

            # 2. 任务规划
            self.mcp = self.task_planner.process(self.mcp, self.strategies)
            
            # 3. 命令执行
            if self.mcp.executable_command:
                self.mcp = self.tool_executor.execute(self.mcp)
            else:
                print("Warning: No executable command planned. Skipping execution.")
                break

            # 4. 战术反思 (预测验证)
            is_prediction_met = self.prediction_verifier.verify(self.mcp)
            
            if is_prediction_met:
                print("Prediction met. Archiving results and proceeding.")
                # 创建一个规范的ExecutionLogEntry对象
                log_entry = {
                    "subgoal": self.mcp.current_subgoal,
                    "summary": self.mcp.working_memory.get("summary", ""),
                    "data_pointers": self.mcp.working_memory.get("data_pointers", {}),
                    "status": "Success"
                }
                self.mcp.execution_history.append(log_entry)
                self.mcp.working_memory = {} # 清空工作内存
                self.mcp.current_strategy_plan.pop(0) # 移除已完成的步骤
            else:
                print("Prediction not met. Updating execution policy for replanning.")
                failure_feedback = f"The command '{self.mcp.executable_command}' failed to produce data matching schema '{self.mcp.expected_data}'."
                self.strategies.execution_policy.append(failure_feedback)
        
        # 5. 所有战略步骤完成后，进行战略反思 (需求验证)
        is_requirements_met = self.requirements_verifier.verify(self.mcp)

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
