# -*- coding: utf-8 -*-
"""
筛选与摘要器 - 将“重型”原始数据转化为轻量级的、高信息密度的摘要。
"""
from Data.mcp_models import MCP
from Entities.base_llm_entity import BaseLLMEntity
from Interfaces.llm_api_interface import OpenAIInterface
from Interfaces.database_interface import RedisClient

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

        # 限制输入长度，防止超出模型限制
        prompt = self.prompt_template.replace('{{raw_data}}', str(raw_data)[:8000])
        
        summary = self.llm_interface.get_completion(prompt, model="gpt-3.5-turbo")
        
        if summary:
            print(f"Generated summary: {summary}")
        else:
            print("Error: LLMFilterSummary received no response.")
            summary = "" #确保返回字符串
        
        return summary

if __name__ == "__main__":
    mcp = MCP(
    session_id="test_session_002",
    user_requirements="预测2030年中国人口"
    )
    raw_data = "This is a test raw data."
    llm_filter_summary = LLMFilterSummary(llm_interface=OpenAIInterface(), db_interface=RedisClient())
    summary = llm_filter_summary.process(mcp, raw_data)
    print(summary)