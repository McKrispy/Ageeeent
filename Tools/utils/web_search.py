# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from ddgs import DDGS
import requests
import json

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

    def execute(self, mcp: MCP, keywords: list, num_results: int = 5, **kwargs) -> dict:
        """
        执行完整的搜索、存储和摘要流程。
        :param mcp: 当前的 MCP 实例。
        :param keywords: 搜索关键词列表。
        :param num_results: 需要返回的搜索结果数量。
        :return: 一个包含 'summary' 和 'data_key' 的字典。
        """
        print(f"WebSearchTool: Starting web search with keywords: {keywords}")

        # 1. 执行搜索并获取原始内容
        html_results = self._search(keywords, num_results)
        content_results = self._extract_content(html_results)
        
        # 将所有内容结果合并为一个字符串
        raw_data_str = json.dumps(content_results, indent=2)

        # 2. 生成唯一的 Redis 键
        # 格式: session_id:global_cycle_count:tool_id:instance_id
        data_key = f"{mcp.session_id}:{mcp.global_cycle_count}:{self.tool_id}:{self.instance_id}"
        
        # 3. 将原始数据存入 Redis
        print(f"WebSearchTool: Storing raw content in Redis with key: {data_key}")
        self.db_interface.store_data(data_key, {"content": raw_data_str})
        
        # 4. 调用 LLMFilterSummary 生成摘要
        print("WebSearchTool: Calling LLMFilterSummary to generate summary...")
        summary = self.llm_summarizer.process(mcp, raw_data=raw_data_str)
        
        # 5. 返回摘要和数据键给 Executor
        print("WebSearchTool: Execution complete. Returning summary and data key.")
        return {
            "summary": summary,
            "data_key": data_key
        }

    def _search(self, keywords: list, num_results: int) -> list:
        """
        使用 DuckDuckGo 执行搜索并获取 HTML 页面。
        """
        query = " ".join(keywords)
        html_results = []
        print(f"WebSearchTool: Performing search for '{query}'...")
        with DDGS() as ddgs:
            for result in ddgs.text(query, max_results=num_results):
                url = result.get("href")
                if not url:
                    continue
                try:
                    response = requests.get(url, timeout=10, headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                    })
                    response.raise_for_status()
                    html_results.append({
                        "url": url,
                        "html": response.text
                    })
                except requests.RequestException as e:
                    print(f"WebSearchTool: Failed to fetch {url}: {e}")
        return html_results

    def _extract_content(self, html_results: list) -> list:
        """
        从 HTML 中提取正文内容。
        """
        content_results = []
        print("WebSearchTool: Extracting content from fetched HTMLs...")
        for item in html_results:
            url = item["url"]
            html = item["html"]
            try:
                soup = BeautifulSoup(html, "html.parser")
                # 移除脚本、样式、导航等非主要内容元素
                for tag in soup(["script", "style", "nav", "footer", "aside", "form"]):
                    tag.decompose()
                
                text = soup.get_text(separator=" ", strip=True)
                clean_text = ' '.join(text.split())
                
                content_results.append({
                    "url": url,
                    "content": clean_text
                })
            except Exception as e:
                print(f"WebSearchTool: Error parsing content from {url}: {e}")
        return content_results


'''if __name__ == "__main__":
    web_search_tool = WebSearchTool()
    results = web_search_tool.execute(keywords=["python", "programming"], num_results=2)
    print(results)
'''