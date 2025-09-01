# -*- coding: utf-8 -*-
"""
Filter and Summarizer - Converts "heavy" raw data into lightweight, high information density summaries.
"""
from Data.mcp_models import MCP
from Entities.base_llm_entity import BaseLLMEntity
from Interfaces.llm_api_interface import OpenAIInterface, GoogleCloudInterface
from Interfaces.database_interface import RedisClient
# from Interfaces.database_interface import RedisClient

class LLMFilterSummary(BaseLLMEntity):
    """
    Filter and Summarizer - Converts "heavy" raw data into lightweight, high information density summaries.
    """
    def process(self, mcp: MCP, raw_data: str) -> str:
        """
        Process raw data and generate summary.
        :param mcp: MCP object for status updates.
        :param raw_data: Raw data string from tools.
        :return: Returns the generated summary string.
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
