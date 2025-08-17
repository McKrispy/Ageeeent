"""
异步工作流管理器 - 支持实时控制和状态管理
"""
import asyncio
import threading
import time
from typing import Optional, Callable
from GUI.utils.logger import WorkflowLogger
from GUI.utils.config import LLMConfig

# 导入工作流所需的模块
from Data.mcp_models import MCP, WorkingMemory, StrategyPlan, SubGoal, ExecutableCommand
from Data.strategies import StrategyData
from Interfaces.llm_api_interface import OpenAIInterface, GoogleCloudInterface, AnthropicInterface
from Interfaces.database_interface import RedisClient
from Entities.strategy_planner import LLMStrategyPlanner
from Entities.task_planner import LLMTaskPlanner
from Entities.questionnaire_designer import QuestionnaireDesigner
from Entities.profile_drawer import ProfileDrawer
from Entities.filter_summary import LLMFilterSummary
from Tools.executor import ToolExecutor
from Tools.tool_registry import ToolRegistry

class AsyncWorkflowManager:
    """工作流管理器"""
    
    def __init__(self):
        self.workflow_task: Optional[asyncio.Task] = None
        self.workflow_thread: Optional[threading.Thread] = None
        self.is_running = False
        self.should_stop = False
        self.logger = WorkflowLogger()
        self.progress_callback: Optional[Callable] = None
        
        # 工作流状态
        self.mcp: Optional[MCP] = None
        self.working_memory: Optional[WorkingMemory] = None
        self.strategies: Optional[StrategyData] = None
        self.waiting_for_supplementary = False
        self.questionnaire_data = None
        self.supplementary_info = None
        
        # 初始化接口和实体（延迟初始化）
        self.llm_interface: Optional[OpenAIInterface | GoogleCloudInterface | AnthropicInterface] = None
        self.db_interface: Optional[RedisClient] = None
        self.questionnaire_designer: Optional[QuestionnaireDesigner] = None
        self.profile_drawer: Optional[ProfileDrawer] = None
        self.strategy_planner: Optional[LLMStrategyPlanner] = None
        self.task_planner: Optional[LLMTaskPlanner] = None
        self.filter_summary: Optional[LLMFilterSummary] = None
        self.executor: Optional[ToolExecutor] = None
        self.tool_registry: Optional[ToolRegistry] = None
    
    def start_workflow(self, user_input: str, progress_callback: Optional[Callable] = None):
        """启动工作流"""
        if self.is_running:
            return False
        
        self.is_running = True
        self.should_stop = False
        self.progress_callback = progress_callback
        
        # 在线程中运行工作流
        self.workflow_thread = threading.Thread(
            target=self.execute_workflow,
            args=(user_input,)
        )
        self.workflow_thread.daemon = True
        self.workflow_thread.start()
        
        return True
    
    def stop_workflow(self):
        """停止工作流"""
        if not self.is_running:
            return
        
        self.should_stop = True
        self.is_running = False
        
        # 等待工作流线程结束
        if self.workflow_thread and self.workflow_thread.is_alive():
            self.workflow_thread.join(timeout=5)
        
        # 清理资源
        if self.db_interface:
            try:
                self.db_interface.disconnect()
            except:
                pass
        
        self.logger.add_log("system", "工作流已停止", "warning")
    
    def execute_workflow(self, user_input: str) -> bool:
        """执行工作流步骤"""
        session_id = f"session_{int(time.time())}"
        
        try:
            # ==================== 第1条：系统初始化 ====================
            if not self._check_stop_and_log("Initialization", "开始系统初始化..."):
                return False
            
            # 1.1-1.2: 初始化接口
            if not self._check_stop_and_log("Initialization", "1.1-1.2: 初始化LLM接口和数据库接口..."):
                return False

            selected_provider = LLMConfig.get_general_config()['selected_provider']
            
            if selected_provider == "OpenAI":
                self.llm_interface = OpenAIInterface()
            elif selected_provider == "Google":
                self.llm_interface = GoogleCloudInterface()
            elif selected_provider == "Anthropic":
                self.llm_interface = AnthropicInterface()
            
            self.db_interface = RedisClient()
            self.logger.add_log("Initialization", "✅ LLM接口和数据库接口初始化完成", "success")
            
            # 1.3: 初始化数据类
            if not self._check_stop_and_log("Initialization", "1.3: 初始化数据类..."):
                return False
            
            self.mcp = MCP(user_requirements=user_input, session_id=session_id)
            self.working_memory = WorkingMemory()
            self.strategies = StrategyData()
            self.logger.add_log("Initialization", "✅ MCP、WorkingMemory、StrategyData初始化完成", "success")
            
            # 1.4: 初始化实体
            if not self._check_stop_and_log("Initialization", "1.4: 初始化LLM实体..."):
                return False
            
            self.questionnaire_designer = QuestionnaireDesigner(self.llm_interface, self.db_interface)
            self.profile_drawer = ProfileDrawer(self.llm_interface, self.db_interface)
            self.strategy_planner = LLMStrategyPlanner(self.llm_interface, self.db_interface)
            self.task_planner = LLMTaskPlanner(self.llm_interface, self.db_interface)
            self.filter_summary = LLMFilterSummary(self.llm_interface, self.db_interface)
            self.logger.add_log("Initialization", "✅ 所有LLM实体初始化完成", "success")
            
            # 1.5: 初始化工具注册表
            if not self._check_stop_and_log("Initialization", "1.5: 初始化工具注册表..."):
                return False
            
            self.executor = ToolExecutor(self.db_interface, self.filter_summary)
            self.tool_registry = ToolRegistry()
            available_tools = self.tool_registry.list_tools()
            self.logger.add_log("Initialization", f"✅ 工具注册表初始化完成，可用工具: {available_tools}", "success")
            
            # ==================== 第2条：接收用户原始输入 ====================
            if not self._check_stop_and_log("User Input", "第2条：接收用户原始输入"):
                return False
            
            self.logger.add_log("User Input", f"用户需求: {user_input}", "info")
            self.logger.add_log("User Input", "✅ 用户原始输入已接收", "success")
            
            # ==================== 第3条：生成问题 ====================
            if not self._check_stop_and_log("Questionnaire Designer", "第3条：questionnaire_designer生成问题"):
                return False
            
            questionnaire = self.questionnaire_designer.process(self.mcp)
            self.logger.add_log("Questionnaire Designer", f"生成的问题清单:\n{questionnaire}", "info")
            
            self.questionnaire_data = questionnaire
            self.waiting_for_supplementary = True
            self.logger.add_log("Questionnaire Designer", "⏳ 等待用户完成问卷...", "info")

            supplementary_info = self._manage_questionnaire_interaction(action="wait")
            
            # ==================== 第4条：用户画像分析 ====================
            if not self._check_stop_and_log("Profile Drawer", "第4条：profile_drawer分析用户画像"):
                return False
            
            self.mcp = self.profile_drawer.process(self.mcp, supplementary_info)
            
            if self.mcp.completion_requirement:
                self.logger.add_log("Profile Drawer", f"用户画像: {self.mcp.completion_requirement.profile_analysis}", "info")
            
            self.logger.add_log("Profile Drawer", "✅ 用户画像分析完成", "success")
            
            # ==================== 第5条：开始双重循环 ====================
            if not self._check_stop_and_log("Double Loop", "第5条：开始双重循环（用户信息输入完成）"):
                return False
            
            self.logger.add_log("Double Loop", "✅ 用户信息输入阶段完成，开始进入嵌套双重循环", "success")
            
            # ==================== 第6条：战略规划 ====================
            if not self._check_stop_and_log("Strategy Planner", "第6条：strategy_planner生成战略计划"):
                return False
            
            self.mcp = self.strategy_planner.process(self.mcp, self.strategies)
            
            self.logger.add_log("Strategy Planner", f"✅ 战略计划生成完成 ({len(self.mcp.strategy_plans)}个计划)", "success")
            
            # ==================== 第7条：任务规划 ====================
            if not self._check_stop_and_log("Task Planner", "第7条：task_planner生成子目标和执行命令"):
                return False
            
            self.mcp = self.task_planner.process(self.mcp, self.strategies)

            self.logger.add_log("Task Planner", f"✅ 子目标和执行命令生成完成 ({len(self.mcp.sub_goals)}个子目标, {len(self.mcp.executable_commands)}个命令)", "success")
            
            # ==================== 第8条：执行命令 ====================
            if not self._check_stop_and_log("Execution", "第8条：执行命令"):
                return False
            
            is_executed = self.executor.execute(self.mcp, self.working_memory)
            if not is_executed:
                self.logger.add_log("Execution", "❌ 执行命令失败", "error")
                return False
            
            self.logger.add_log("Execution", f"✅ 执行命令完成 ({len(self.mcp.executable_commands)}个命令)", "success")
            self.logger.add_log("Execution", f"执行命令结果: {self.working_memory.data}", "info")
            
            # ==================== 第9条：总结 ====================
            self.logger.add_log("Summary", "✅ 工作流执行完成", "success")
            return True
            
        except Exception as e:
            self.logger.add_log("system", f"工作流执行出错: {str(e)}", "error")
            return False
    
    def _check_stop_and_log(self, phase: str, message: str) -> bool:
        """检查是否应该停止并记录日志"""
        if self.should_stop:
            self.logger.add_log("system", f"工作流在{phase}阶段被停止", "warning")
            return False
        
        self.logger.add_log(phase, message, "info")
        return True
    
    def _manage_questionnaire_interaction(self, action: str = "check", info: str = None) -> str:
        """
        管理问卷交互的统合方法
        
        Args:
            action: 操作类型 - "check"(检查状态), "submit"(提交信息), "get"(获取问卷)
            info: 当action为"submit"时，要提交的补充信息
        
        Returns:
            根据action返回相应的结果
        """
        if action == "check":
            # 检查是否正在等待用户完成问卷
            return self.waiting_for_supplementary
        
        elif action == "submit":
            # 提交补充信息
            if info:
                self.supplementary_info = info
                self.waiting_for_supplementary = False
                self.logger.add_log("User Input", f"用户提交补充信息: {info[:100]}...", "success")
                return "success"
            return "error"
        
        elif action == "get":
            # 获取当前问卷数据
            return self.questionnaire_data or ""
        
        elif action == "wait":
            # 等待用户完成问卷
            while self.waiting_for_supplementary and not self.should_stop:
                time.sleep(0.5)  # 短暂休眠避免CPU占用过高
            
            if self.should_stop:
                return ""
            
            return self.supplementary_info or ""
        
        else:
            return "invalid_action"
    
    def get_workflow_results(self) -> dict:
        """获取工作流执行结果"""
        if not self.mcp:
            return {}
        
        return {
            "strategy_plans": len(self.mcp.strategy_plans) if self.mcp.strategy_plans else 0,
            "sub_goals": len(self.mcp.sub_goals) if self.mcp.sub_goals else 0,
            "executable_commands": len(self.mcp.executable_commands) if self.mcp.executable_commands else 0,
            "mcp": self.mcp,
            "working_memory": self.working_memory,
            "strategies": self.strategies
        }
    
    def get_status(self) -> dict:
        """获取工作流状态"""
        return {
            "is_running": self.is_running,
            "should_stop": self.should_stop,
            "logger": self.logger,
            "results": self.get_workflow_results()
        }
    
    def is_workflow_running(self) -> bool:
        """检查工作流是否正在运行"""
        return self.is_running
