# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from ddgs import DDGS
import requests
import json

from Interfaces.llm_api_interface import OpenAIInterface
from Tools.utils.base_tool import BaseTool
from Data.mcp_models import MCP
from Interfaces.database_interface import RedisClient
from Entities.filter_summary import LLMFilterSummary

class WebSearchTool(BaseTool):
    """
    WebSearchTool 负责执行网络搜索、提取内容、存储原始数据，并调用摘要器。
    """
    def __init__(self, db_interface: RedisClient, llm_summarizer: LLMFilterSummary):
        """
        初始化 WebSearchTool。
        :param db_interface: RedisClient 的实例，用于与数据库交互。
        :param llm_summarizer: LLMFilterSummary 的实例，用于生成摘要。
        """
        super().__init__(db_interface, llm_summarizer)
        if not self.db_interface:
            print("WebSearchTool: No database interface provided!")
        else:
            print(f"WebSearchTool: Database interface connected with host: {self.db_interface.host}, port: {self.db_interface.port}, db: {self.db_interface.db}")

    def execute(self, mcp: MCP, keywords: list, num_results: int = 3, **kwargs) -> dict:
        """
        执行完整的搜索、存储和摘要流程。
        :param keywords: 搜索关键词列表。
        :param num_results: 需要返回的搜索结果数量。
        :return: 一个包含 'summary' 和 'data_key' 的字典。
        """
        # 1. 执行搜索并获取原始内容
        content_results = self._search_and_extract(keywords, num_results)
        
        # 将所有内容结果合并为一个字符串
        raw_data_str = json.dumps(content_results, indent=2)

        # 2. 生成唯一的 Redis 键
        # 格式: session_id:global_cycle_count:tool_id:instance_id
        data_key = f"{mcp.session_id}:{mcp.global_cycle_count}:{self.tool_id}:{self.instance_id}"
        
        # 3. 将原始数据存入 Redis
        self.db_interface.store_data(data_key, content_results)
        
        # 4. 调用 LLMFilterSummary 生成摘要
        summary = self.llm_summarizer.process(mcp, raw_data=raw_data_str)
        
        # 5. 返回摘要和数据键给 Executor
        return {
            data_key: summary
        }

    def _search_and_extract(self, keywords: list, num_results: int) -> list[dict]:
        """
        Fetch pages and extract clean text in one pass.
        Returns: [{"url": str, "content": str}, ...]
        """
        query = " ".join(keywords)
        results: list[dict] = []
        with DDGS() as ddgs:
            for hit in ddgs.text(query, max_results=num_results):
                url = hit.get("href")
                if not url:
                    continue
                try:
                    resp = requests.get(
                        url,
                        timeout=10,
                        headers={"User-Agent": "Mozilla/5.0 Chrome/123 Safari/537.36"},
                    )
                    resp.raise_for_status()
                    soup = BeautifulSoup(resp.text, "html.parser")
                    # remove non-content tags
                    for tag in soup(["script", "style", "nav", "footer", "aside", "form"]):
                        tag.decompose()
                    text = " ".join(soup.get_text(separator=" ", strip=True).split())
                    if text:
                        results.append({"url": url, "content": text})
                except requests.RequestException as e:
                    print(f"WebSearchTool: Failed to fetch {url}: {e}")
        return results
    
if __name__ == "__main__":
    db_interface = RedisClient()
    llm_interface = OpenAIInterface()
    llm_summarizer = LLMFilterSummary(llm_interface, db_interface, "test_filter_summary")
    web_search_tool = WebSearchTool(db_interface, llm_summarizer)
    web_search_tool.execute(["python", "programming"])