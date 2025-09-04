# -*- coding: utf-8 -*-
"""
This file defines the abstract base class for all LLM entities.
"""
import os
from abc import ABC, abstractmethod
from typing import Any
import uuid

from Data.mcp_models import MCP
from Interfaces.llm_api_interface import LLMAPIInterface
from Interfaces.database_interface import DatabaseInterface

class BaseLLMEntity(ABC):
    """
    Abstract base class for all LLM entities.
    It handles communication with LLM interfaces and prompt loading, and manages its own state.
    """
    def __init__(self, llm_interface: LLMAPIInterface, db_interface: DatabaseInterface = None, entity_id: str = None):
        self.llm_interface = llm_interface
        self.db_interface = db_interface
        self.prompt_template = self._load_prompt()
        
        self.entity_id = entity_id or f"{self.__class__.__name__}_{uuid.uuid4()}"


    def _load_prompt(self) -> str:
        """
        从 'prompts' 目录加载与类名对应的 prompt 文件。
        例如，LLMStrategyPlanner -> prompts/strategy_planner_prompt.txt
        """
        # 从类名推断文件名 (e.g., LLMStrategyPlanner -> strategy_planner)
        class_name = self.__class__.__name__
        if class_name.startswith("LLM"):
            class_name = class_name[3:] # Remove "LLM"
        
        prompt_name_base = ''.join(['_' + i.lower() if i.isupper() else i for i in class_name]).lstrip('_')
        prompt_name = f"{prompt_name_base}_prompt.txt"

        try:
            # 构造相对于当前文件位置的路径
            current_dir = os.path.dirname(os.path.abspath(__file__))
            prompt_path = os.path.join(current_dir, '..', 'Prompts', prompt_name)
            
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"Warning: Prompt file not found for {self.__class__.__name__} at {prompt_path}")
            return ""

    def retrieve_from_db(self, key: str) -> Any:
        """
        从 RedisJSON 数据库中检索信息。
        """
        if self.db_interface:
            return self.db_interface.retrieve_data(key)
        print("Warning: Database interface not configured.")
        return None

    @abstractmethod
    def process(self, mcp: MCP, *args, **kwargs) -> MCP:
        """
        所有实体都必须实现此方法来处理 MCP 对象。
        """
        pass
