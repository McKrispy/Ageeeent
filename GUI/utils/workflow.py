"""
Asynchronous workflow manager - supports real-time control and state management
"""
import asyncio
import threading
import time
from typing import Optional, Callable
from GUI.utils.logger import WorkflowLogger
from GUI.utils.config import LLMConfig

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
        self.questionnaire_data = None
        self.supplementary_info = None
        self.waiting_for_supplementary = False
        
        # 等待工作流线程结束
        if self.workflow_thread and self.workflow_thread.is_alive():
            self.workflow_thread.join(timeout=5)
        
        # 清理资源
        if self.db_interface:
            try:
                self.db_interface.disconnect()
            except:
                pass
        
        self.logger.add_log("system", "Workflow stopped", "warning")
    
    def execute_workflow(self, user_input: str) -> bool:
        session_id = f"session_{int(time.time())}"
        
        try:
            # ==================== 第1条：系统初始化 ====================
            if not self._check_stop_and_log("Initialization", "Starting system initialization..."):
                return False
            
            # 1.1-1.2: 初始化接口
            if not self._check_stop_and_log("Initialization", "1.1-1.2: Initializing LLM interface and database interface..."):
                return False

            selected_provider = LLMConfig.get_general_config()['selected_provider']
            
            if selected_provider == "OpenAI":
                self.llm_interface = OpenAIInterface()
            elif selected_provider == "Google":
                self.llm_interface = GoogleCloudInterface()
            elif selected_provider == "Anthropic":
                self.llm_interface = AnthropicInterface()
            
            self.db_interface = RedisClient()
            self.logger.add_log("Initialization", "✅ LLM interface and database interface initialization completed", "success")
            
            # 1.3: 初始化数据类
            if not self._check_stop_and_log("Initialization", "1.3: Initializing data classes..."):
                return False
            
            self.mcp = MCP(user_requirements=user_input, session_id=session_id)
            self.working_memory = WorkingMemory()
            self.strategies = StrategyData()
            self.logger.add_log("Initialization", "✅ MCP, WorkingMemory, StrategyData initialization completed", "success")
            
            # 1.4: 初始化实体
            if not self._check_stop_and_log("Initialization", "1.4: Initializing LLM entities..."):
                return False
            
            self.questionnaire_designer = QuestionnaireDesigner(self.llm_interface, self.db_interface)
            self.profile_drawer = ProfileDrawer(self.llm_interface, self.db_interface)
            self.strategy_planner = LLMStrategyPlanner(self.llm_interface, self.db_interface)
            self.task_planner = LLMTaskPlanner(self.llm_interface, self.db_interface)
            self.filter_summary = LLMFilterSummary(self.llm_interface, self.db_interface)
            self.logger.add_log("Initialization", "✅ All LLM entities initialization completed", "success")
            
            # 1.5: 初始化工具注册表
            if not self._check_stop_and_log("Initialization", "1.5: Initializing tool registry..."):
                return False
            
            self.executor = ToolExecutor(self.db_interface, self.filter_summary)
            self.tool_registry = ToolRegistry()
            available_tools = self.tool_registry.list_tools()
            self.logger.add_log("Initialization", f"✅ Tool registry initialization completed, available tools: {available_tools}", "success")
            
            # ==================== 第2条：接收用户原始输入 ====================
            if not self._check_stop_and_log("User Input", "2: Receiving user original input..."):
                return False
            
            self.logger.add_log("User Input", f"User requirements: {user_input}", "info")
            self.logger.add_log("User Input", "✅ User original input received", "success")
            
            # ==================== 第3条：生成问题 ====================
            if not self._check_stop_and_log("Questionnaire Designer", "3: questionnaire_designer generating questions..."):
                return False
            
            questionnaire = self.questionnaire_designer.process(self.mcp)
            self.logger.add_log("Questionnaire Designer", f"Generated questionnaire:\n{questionnaire}", "info")
            
            self.questionnaire_data = questionnaire
            self.waiting_for_supplementary = True
            self.logger.add_log("Questionnaire Designer", "⏳ Waiting for user to complete questionnaire...", "info")

            supplementary_info = self._manage_questionnaire_interaction(action="wait")
            
            # ==================== 第4条：用户画像分析 ====================
            if not self._check_stop_and_log("Profile Drawer", "4: profile_drawer analyzing user profile..."):
                return False
            
            self.mcp = self.profile_drawer.process(self.mcp, supplementary_info)
            
            if self.mcp.completion_requirement:
                self.logger.add_log("Profile Drawer", f"User profile: {self.mcp.completion_requirement.profile_analysis}", "info")
            
            self.logger.add_log("Profile Drawer", "✅ User profile analysis completed", "success")
            
            # ==================== 第5条：开始双重循环 ====================
            if not self._check_stop_and_log("Double Loop", "5: Starting double loop (user information input completed)"):
                return False
            
            self.logger.add_log("Double Loop", "✅ User information input stage completed, starting nested double loop", "success")
            
            # ==================== 第6条：战略规划 ====================
            if not self._check_stop_and_log("Strategy Planner", "6: strategy_planner generating strategy plan..."):
                return False
            
            self.mcp = self.strategy_planner.process(self.mcp, self.strategies)
            
            self.logger.add_log("Strategy Planner", f"✅ Strategy plan generation completed ({len(self.mcp.strategy_plans)} plans)", "success")
            
            # ==================== 第7条：任务规划 ====================
            if not self._check_stop_and_log("Task Planner", "7: task_planner generating sub-goals and execution commands..."):
                return False
            
            self.mcp = self.task_planner.process(self.mcp, self.strategies)

            self.logger.add_log("Task Planner", f"✅ Sub-goals and execution commands generation completed ({len(self.mcp.sub_goals)} sub-goals, {len(self.mcp.executable_commands)} commands)", "success")
            
            # ==================== 第8条：执行命令 ====================
            if not self._check_stop_and_log("Execution", "8: executing commands..."):
                return False
            
            is_executed = self.executor.execute(self.mcp, self.working_memory)
            if not is_executed:
                self.logger.add_log("Execution", "❌ Command execution failed", "error")
                return False
            
            self.logger.add_log("Execution", f"✅ Command execution completed ({len(self.mcp.executable_commands)} commands)", "success")
            self.logger.add_log("Execution", f"Command execution result: {self.working_memory.data}", "info")
            
            # ==================== 第9条：总结 ====================
            self.logger.add_log("MCP", f"✅ Final MCP: {self.mcp}", "info")
            self.logger.add_log("Summary", "✅ Workflow execution completed", "success")
            return True
            
        except Exception as e:
            self.logger.add_log("system", f"Workflow execution error: {str(e)}", "error")
            return False
    
    def _check_stop_and_log(self, phase: str, message: str) -> bool:
        if self.should_stop:
            self.logger.add_log("system", f"Workflow stopped at {phase} phase", "warning")
            return False
        
        self.logger.add_log(phase, message, "info")
        return True
    
    def _manage_questionnaire_interaction(self, action: str = "check", info: str = None) -> str:
        """
        Management of questionnaire interaction
        
        Args:
            action: Operation type - "check"(check status), "submit"(submit information), "get"(get questionnaire)
            info: When action is "submit", the supplementary information to be submitted
        
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
                self.logger.add_log("User Input", f"User submitted supplementary information: {info[:100]}...", "success")
                return "success"
            return "error"
        
        elif action == "get":
            # Get current questionnaire data
            return self.questionnaire_data or ""
        
        elif action == "wait":
            # Wait for user to complete questionnaire
            while self.waiting_for_supplementary and not self.should_stop:
                time.sleep(0.5)  # Short sleep to avoid high CPU usage
            
            if self.should_stop:
                return ""
            
            return self.supplementary_info or ""
        
        else:
            return "invalid_action"
    
    def get_workflow_results(self) -> dict:
        """Get workflow execution results"""
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
        """Get workflow status"""
        return {
            "is_running": self.is_running,
            "should_stop": self.should_stop,
            "logger": self.logger,
            "results": self.get_workflow_results()
        }
    
    def is_workflow_running(self) -> bool:
        """Check if workflow is running"""
        return self.is_running
