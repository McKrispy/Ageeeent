# -*- coding: utf-8 -*-
"""
此文件定义了所有 LLM 实体的抽象基类。
"""
import os
from abc import ABC, abstractmethod
from typing import Any

from Data.mcp_models import MCP
from Interfaces.llm_api_interface import LLMAPIInterface
from Interfaces.database_interface import DatabaseInterface

class BaseLLMEntity(ABC):
    """
    所有 LLM 实体的抽象基类。
    它处理与 LLM 接口的通信和 Prompt 的加载。
    """
    def __init__(self, llm_interface: LLMAPIInterface, db_interface: DatabaseInterface = None):
        self.llm_interface = llm_interface
        self.db_interface = db_interface
        self.prompt_template = self._load_prompt()

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
            prompt_path = os.path.join(current_dir, '..', 'prompts', prompt_name)
            
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
    def process(self, mcp: MCP) -> MCP:
        """
        所有实体都必须实现此方法来处理 MCP 对象。
        """
        pass
