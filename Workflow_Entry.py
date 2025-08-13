# -*- coding: utf-8 -*-
"""
整个工作流的入口，负责接收用户需求并驱动所有 LLM 实体，实现完整的“研究-执行-反思”闭环。
"""
import json
from typing import Optional

from Data.mcp_models import MCP, WorkingMemory, ExecutableCommand
from Data.strategies import StrategyData
from Interfaces.llm_api_interface import OpenAIInterface
from Interfaces.database_interface import RedisClient
from Entities.strategy_planner import LLMStrategyPlanner
from Entities.task_planner import LLMTaskPlanner
from Entities.questionnaire_designer import QuestionnaireDesigner
from Entities.profile_drawer import ProfileDrawer
from Entities.filter_summary import LLMFilterSummary
from Entities.verification_entities import PredictionVerification, RequirementsVerification
from Tools.tool_registry import ToolRegistry
from Tools.executor import ToolExecutor


class AgentWorkflow:
    """
    整个工作流的入口，负责接收用户需求并驱动所有 LLM 实体。
    """
    def __init__(self, user_requirements: str, session_id: str):
        # 1.1 - 1.3: 初始化接口和数据类
        self.llm_interface = OpenAIInterface()
        self.db_interface = RedisClient()
        self.mcp = MCP(user_requirements=user_requirements, session_id=session_id)
        self.working_memory = WorkingMemory()
        self.strategies = StrategyData()

        # 1.4: 初始化实体
        self.questionnaire_designer = QuestionnaireDesigner(self.llm_interface, self.db_interface)
        self.profile_drawer = ProfileDrawer(self.llm_interface, self.db_interface)
        self.strategy_planner = LLMStrategyPlanner(self.llm_interface)
        self.task_planner = LLMTaskPlanner(self.llm_interface)

        # 1.5: 初始化工具注册表
        self.tool_registry = ToolRegistry()
        # 工具已经在ToolRegistry中自动注册，无需额外注册

    def _find_next_command(self) -> Optional[ExecutableCommand]:
        """查找下一个未执行的命令。"""
        for command in self.mcp.executable_commands:
            if not command.is_completed:
                return command
        return None

    def _update_completion_status(self, completed_command: ExecutableCommand):
        """更新命令、子目标和战略计划的完成状态。"""
        completed_command.is_completed = True

        # 检查父子目标是否完成
        sub_goal = next((sg for sg in self.mcp.sub_goals if sg.id == completed_command.parent_sub_goal_id), None)
        if sub_goal:
            all_commands_for_sub_goal = [cmd for cmd in self.mcp.executable_commands if cmd.parent_sub_goal_id == sub_goal.id]
            if all(cmd.is_completed for cmd in all_commands_for_sub_goal):
                sub_goal.is_completed = True
                print(f"--- Sub-goal '{sub_goal.description}' COMPLETED ---")

                # 检查父战略计划是否完成
                strategy_plan = next((sp for sp in self.mcp.strategy_plans if sp.id == sub_goal.parent_strategy_plan_id), None)
                if strategy_plan:
                    all_sub_goals_for_plan = [sg for sg in self.mcp.sub_goals if sg.parent_strategy_plan_id == strategy_plan.id]
                    if all(sg.is_completed for sg in all_sub_goals_for_plan):
                        strategy_plan.is_completed = True
                        print(f"--- Strategy Plan '{strategy_plan.description}' COMPLETED ---")

    def run(self):
        """
        启动并执行整个 Agent 工作流，采用最高效的扁平化、状态驱动模型。
        """
        print(f"--- Starting Agent Workflow for Session ID: {self.mcp.session_id} ---")
        print(f"User Requirements: {self.mcp.user_requirements}")
        
        try:
            self.db_interface.connect()

            # 2 & 3: 处理用户输入并生成问题
            print("\n--- Phase 1: User Input Processing ---")
            questionnaire = self.questionnaire_designer.process(self.mcp)
            
            # 模拟用户补充信息
            # 在实际应用中，这里会有一个与用户交互的步骤
            print(f"Generated Questionnaire: {questionnaire}")
            supplementary_info = input("Please provide supplementary information based on the questionnaire above: ")

            # 4: 生成用户画像并更新MCP
            self.mcp = self.profile_drawer.process(self.mcp, supplementary_info)
            print("--- User Input Processing Complete ---")


            # 6 & 7: 规划阶段
            print("\n--- Phase 2: Planning ---")
            self.mcp = self.strategy_planner.process(self.mcp, self.strategies)
            self.mcp = self.task_planner.process(self.mcp, self.strategies)
            print("--- Planning Complete ---")

            # 8: 执行阶段
            print("\n--- Phase 3: Execution ---")
            tool_executor = ToolExecutor(db_interface=self.db_interface, 
                                     llm_summarizer=LLMFilterSummary(self.llm_interface))
            prediction_verifier = PredictionVerification()

            while self._find_next_command():
                command_to_execute = self._find_next_command()
                if not command_to_execute:
                    break

                # 8: 执行命令 - executor负责实例化工具并将结果写入working_memory
                execution_success = tool_executor.execute(command_to_execute, self.mcp.session_id, self.working_memory)
                
                if execution_success:
                    print(f"Successfully executed command: {command_to_execute.id}")
                    
                    # 验证并可能进行总结（可选的额外处理）
                    # 注意：数据已经由executor写入working_memory了
                    for redis_key, raw_data in self.working_memory.data.items():
                        if prediction_verifier.verify(raw_data):
                            # 如果需要总结，可以调用LLMFilterSummary
                            summary = tool_executor.llm_summarizer.process(raw_data)
                            self.working_memory.data[redis_key] = summary
                else:
                    print(f"Failed to execute command: {command_to_execute.id}")

                self._update_completion_status(command_to_execute)

            # 9. 验证阶段
            print("\n--- Phase 4: Verification ---")
            requirements_verifier = RequirementsVerification()
            if requirements_verifier.verify(self.mcp, self.working_memory):
                print("--- All requirements satisfied. Workflow complete. ---")
            else:
                print("--- Some requirements not satisfied. Looping back for replanning. ---")
                self.mcp.executable_commands = [] # 清空命令列表以重新规划
                self.run()  # 重新运行工作流

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            self.db_interface.disconnect()
            print(f"--- Agent Workflow for Session ID: {self.mcp.session_id} Finished ---")

if __name__ == '__main__':
    # 示例用法
    user_req = "Find the latest research on AI-driven drug discovery and summarize the top 3 findings."
    session_id = "session_12345"
    workflow = AgentWorkflow(user_requirements=user_req, session_id=session_id)
    workflow.run()
