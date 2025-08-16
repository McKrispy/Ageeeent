from abc import ABC, abstractmethod
from typing import Any
import uuid

from Interfaces.database_interface import RedisClient
from Entities.filter_summary import LLMFilterSummary
from Data.mcp_models import MCP, WorkingMemory, ExecutableCommand

class BaseTool(ABC):
    """
    所有工具的抽象基类。
    现在，它要求在实例化时传入一个 RedisClient 实例和一个 LLMFilterSummary 实例。
    """
    def __init__(self, db_interface: RedisClient, llm_summarizer: LLMFilterSummary):
        if not isinstance(db_interface, RedisClient):
            raise TypeError("db_interface must be an instance of RedisClient")
        if not isinstance(llm_summarizer, LLMFilterSummary):
            raise TypeError("llm_summarizer must be an instance of LLMFilterSummary")

        self.tool_id: str = self.__class__.__name__
        self.instance_id: str = uuid.uuid4()
        self.db_interface = db_interface
        self.llm_summarizer = llm_summarizer

    @abstractmethod
    def execute(self, mcp: MCP, executable_command: ExecutableCommand, **kwargs) -> dict:
        """
        执行工具的具体逻辑。
        子类必须实现此方法。
        该方法现在需要接收一个 MCP 对象，并返回一个包含执行结果的字典。
        返回的字典应至少包含 'summary' 和 'data_key'。
        """
        pass

    def get_instance_id(self) -> str:
        """
        返回此工具实例的唯一ID。
        """
        return self.instance_id
