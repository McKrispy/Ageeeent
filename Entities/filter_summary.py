# -*- coding: utf-8 -*-
"""
筛选与摘要器 - 将“重型”原始数据转化为轻量级的、高信息密度的摘要。
"""
from Data.mcp_models import MCP
from Entities.base_llm_entity import BaseLLMEntity

class LLMFilterSummary(BaseLLMEntity):
    """
    筛选与摘要器 - 将“重型”原始数据转化为轻量级的、高信息密度的摘要。
    """
    def process(self, mcp: MCP) -> MCP:
        """
        处理原始数据，生成摘要，并更新 MCP。
        """
        print("LLMFilterSummary: Summarizing raw data into a lightweight summary.")
        raw_data = mcp.raw_data_from_tool
        
        if not self.prompt_template or not raw_data:
            print("Warning: No prompt or raw data for summary.")
            return mcp

        # 限制输入长度，防止超出模型限制
        prompt = self.prompt_template.replace('{{raw_data}}', str(raw_data)[:8000])
        
        summary = self.llm_interface.get_completion(prompt, model="gpt-3.5-turbo")
        
        # 将摘要存储在 MCP 中，以便后续步骤使用
        if summary:
            mcp.memory_summary.append(summary)
            print(f"Generated summary: {summary}")
        else:
            print("Error: LLMFilterSummary received no response.")

        return mcp
