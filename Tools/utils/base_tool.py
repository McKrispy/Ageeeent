from abc import ABC, abstractmethod
from typing import Any
import uuid

from Interfaces.database_interface import RedisClient
from Entities.filter_summary import LLMFilterSummary
from Data.mcp_models import MCP, WorkingMemory, ExecutableCommand

class BaseTool(ABC):
    """
    Abstract base class for all tools.
    Now it requires passing a RedisClient instance and an LLMFilterSummary instance during instantiation.
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
        Execute the specific logic of the tool.
        Subclasses must implement this method.
        This method now needs to receive an MCP object and return a dictionary containing execution results.
        The returned dictionary should contain at least 'summary' and 'data_key'.
        """
        pass

    def get_instance_id(self) -> str:
        """
        Return the unique ID of this tool instance.
        """
        return self.instance_id
