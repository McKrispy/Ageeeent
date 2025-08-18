# -*- coding: utf-8 -*-
"""
筛选与摘要器 - 将“重型”原始数据转化为轻量级的、高信息密度的摘要。
"""
from Data.mcp_models import MCP
from Entities.base_llm_entity import BaseLLMEntity
from Interfaces.llm_api_interface import OpenAIInterface, GoogleCloudInterface
from Interfaces.database_interface import RedisClient
# from Interfaces.database_interface import RedisClient

class LLMFilterSummary(BaseLLMEntity):
    """
    筛选与摘要器 - 将“重型”原始数据转化为轻量级的、高信息密度的摘要。
    """
    def process(self, mcp: MCP, raw_data: str) -> str:
        """
        处理原始数据，生成摘要。
        :param mcp: MCP对象，用于状态更新。
        :param raw_data: 来自工具的原始数据字符串。
        :return: 返回生成的摘要字符串。
        """

        print("LLMFilterSummary: Summarizing raw data into a lightweight summary.")
        if not self.prompt_template or not raw_data:
            print("Warning: No prompt or raw data for summary.")
            return ""
        prompt = self.prompt_template.replace('{{raw_data}}', str(raw_data)[:8000])
        summary = self.llm_interface.get_completion(prompt, model="gpt-3.5-turbo")
        if summary:
            print(f"LLMFilterSummary: Summary generated successfully.")
        else:
            print("LLMFilterSummary Error: No response.")
            summary = ""
        return summary
