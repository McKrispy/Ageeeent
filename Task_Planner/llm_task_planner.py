import json
from typing import List, Dict, Any, Literal, Optional
from dataclasses import dataclass

# 1. ExpectedData Class Structure
@dataclass
class ExpectedData:
    """
    预期的任务解决所需的数据信息。
    """
    data_type: str  # 例如："json", "text", "image", "table"
    description: str # 对预期数据的文字描述
    schema: Optional[Dict[str, Any]] = None # 如果是结构化数据（如JSON），可以定义其schema
    source_hint: Optional[str] = None # 对数据来源的提示，例如："web_search", "database_api", "user_input"


# 2. LLMConnectionInterface Class
class LLMConnectionInterface:
    """
    负责管理不同LLM服务（LM Studio + Ngrok, Google AI, OpenAI）的连接和请求。
    """
    def __init__(self, provider: Literal["lm_studio", "google_ai", "openai"], api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        初始化LLM连接接口。
        :param provider: LLM提供者类型。
        :param api_key: 如果需要，API密钥。
        :param base_url: LM Studio/Ngrok或其他本地LLM的基准URL。
        """
        pass

    def send_request(self, prompt: str, model: str, temperature: float = 0.7) -> Dict[str, Any]:
        """
        向LLM发送请求并获取响应。
        :param prompt: 发送给LLM的提示。
        :param model: 要使用的LLM模型名称。
        :param temperature: LLM生成响应的温度。
        :return: LLM的原始响应。
        """
        pass

# 3. LLMTaskPlanner Class
class LLMTaskPlanner:
    """
    LLM任务规划器，负责将用户任务分解为子目标，声明预期数据，并生成可执行命令。
    """
    def __init__(self, llm_connection: LLMConnectionInterface):
        """
        初始化LLMTaskPlanner。
        :param llm_connection: 用于与LLM交互的连接接口实例。
        """
        self.llm_connection = llm_connection

    def plan_tasks(self, tasks_json: str) -> List[Dict[str, Any]]:
        """
        接收上层组件传入的JSON格式的优先级并列的tasks，并对它们进行规划。
        :param tasks_json: JSON字符串，包含若干个待处理的任务。
                           示例: '[{"id": "task1", "description": "查找最新股票数据"}, {"id": "task2", "description": "分析用户评论"}]'
        :return: 包含每个任务规划结果的列表，每个结果包含预期的ExpectedData和Executable Normalized Command。
        """
        pass

    def _declare_expected_data(self, task_description: str) -> ExpectedData:
        """
        根据任务描述，利用LLM声明一个ExpectedData实例。
        这个方法将调用LLMConnectionInterface来获取LLM对预期数据的理解。
        :param task_description: 任务的描述。
        :return: 一个ExpectedData实例，包含LLM预测的预期数据信息。
        """
        pass

    def _generate_subgoals(self, task_description: str, expected_data: ExpectedData) -> List[str]:
        """
        根据任务描述和预期数据，利用LLM生成一系列子目标。
        每个子目标负责获取预期数据的一部分。
        :param task_description: 任务的描述。
        :param expected_data: 任务的预期数据信息。
        :return: 子目标描述字符串的列表。
        """
        pass

    def _normalize_to_executable_command(self, subgoals: List[str]) -> Dict[str, Any]:
        """
        将LLM生成的子目标整理为一个规范化可执行的命令格式，供下层Executor执行。
        此方法不直接使用LLM，而是包装LLM的输出。
        :param subgoals: LLM生成的子目标描述列表。
        :return: 符合特定格式的字典，代表可执行命令。
                 示例: {
                     "action": "execute_sequence",
                     "steps": [
                         {"type": "tool_call", "tool_name": "web_search", "parameters": {"query": "..."}},
                         {"type": "data_process", "processor": "ml_model", "parameters": {"data_source": "..."}}
                     ]
                 }
        """
        pass 