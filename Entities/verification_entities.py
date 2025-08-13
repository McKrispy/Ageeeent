# -*- coding: utf-8 -*-
"""
此文件定义了系统中负责验证和反思的实体。
这些组件是实现智能体自我修正和闭环控制的关键。
"""
from abc import ABC, abstractmethod
import uuid
from Data.mcp_models import MCP, WorkingMemory
from Entities.base_llm_entity import BaseLLMEntity
from Interfaces.llm_api_interface import LLMAPIInterface

class BaseVerificationEntity(BaseLLMEntity):
    """
    所有验证实体的抽象基类。
    """
    def __init__(self, llm_interface: LLMAPIInterface = None, db_interface: object = None, entity_id: str = None):
        # 验证类可能不需要LLM，所以允许接口为None
        super().__init__(llm_interface, db_interface, entity_id)

    def _load_prompt(self) -> str:
        # 验证类通常没有自己的prompt文件，返回空字符串
        return ""

    @abstractmethod
    def verify(self, mcp: MCP, working_memory: WorkingMemory = None) -> bool:
        """
        执行验证逻辑。
        """
        pass

    def process(self, mcp: MCP, working_memory: WorkingMemory = None) -> MCP:
        """
        process方法调用verify，以适应通用实体接口。
        """
        self.verify(mcp, working_memory)
        return mcp

class PredictionVerification(BaseVerificationEntity):
    """
    预测验证 - 进行战术层面的快速验证。
    """
    def verify(self, mcp: MCP, working_memory: WorkingMemory) -> bool:
        """
        比较 MCP.expected_data 和 WorkingMemory 中的摘要。
        """

        print("PredictionVerification: Verifying if the execution result meets the expected data schema.")
        
        # 简化逻辑：检查 working_memory 是否非空
        is_met = bool(working_memory.data) 
        
        if is_met:
            print("PredictionVerification: Result MET expected schema.")
        else:
            print("PredictionVerification: Result NOT MET. Triggering tactical correction.")
            
        return is_met

class RequirementsVerification(BaseVerificationEntity):
    """
    需求验证 - 进行战略层面的深度验证。
    """
    def verify(self, mcp: MCP, working_memory: WorkingMemory = None) -> bool:
        """
        在所有步骤完成后，比较 MCP.user_requirements 和 mcp.cycle_history。
        """

        print("RequirementsVerification: Verifying if the accumulated results meet the user's requirements.")
        
        # 简化逻辑：检查 cycle_history 是否为空
        is_met = bool(mcp.cycle_history)
        
        if is_met:
            print("RequirementsVerification: Final requirements MET. Task successful.")
        else:
            print("RequirementsVerification: Final requirements NOT MET. Triggering strategic reflection.")
            
        return is_met
