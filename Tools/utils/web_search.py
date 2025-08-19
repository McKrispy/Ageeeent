# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from ddgs import DDGS
import requests
import json
import time
import random
from trafilatura import fetch_url, extract
from typing import Optional
from Interfaces.llm_api_interface import OpenAIInterface
from Interfaces.database_interface import RedisClient
from Tools.utils.base_tool import BaseTool
from Data.mcp_models import MCP, ExecutableCommand
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

    def execute(self, mcp: MCP, executable_command: ExecutableCommand, **kwargs) -> dict:
        try:
            keywords = executable_command.params.get("keywords")
            num_results = executable_command.params.get("num_results", 3)
            
            if not keywords:
                print("WebSearchTool: No keywords provided")
                return {"error": "No keywords provided"}
            
            if not isinstance(keywords, list):
                print(f"WebSearchTool: Keywords must be a list, got {type(keywords)}")
                return {"error": f"Invalid keywords type: {type(keywords)}"}
            
            content_results = self._search_and_extract(keywords, num_results)
            if not content_results:
                return {"error": "No search results found"}
            raw_data_str = json.dumps(content_results, indent=2, ensure_ascii=False)
            data_key = f"{mcp.session_id}:{mcp.global_cycle_count}:{self.tool_id}:{self.instance_id}"
            self.db_interface.store_data(data_key, content_results)
            summary = self.llm_summarizer.process(mcp, raw_data=raw_data_str)
            return {
                data_key: summary
            }
            
        except Exception as e:
            print(f"WebSearchTool execution error: {e}")
            import traceback
            traceback.print_exc()
            return {"error": f"Execution failed: {str(e)}"}

    def _search_and_extract(self, keywords: list, num_results: int) -> list[dict]:
        try:
            query = " ".join(str(k) for k in keywords if k)
            results = []
            
            with DDGS() as ddgs:
                for hit in ddgs.text(query, max_results=num_results):
                    url = hit.get("href")
                    if not url:
                        continue
                    
                    content = self._trafilatura_extract(url)
                    if content:
                        results.append({"url": url, "content": content})
                    else:
                        print(f"WebSearchTool: Skipping {url} after failed retries")
                        continue
            
            return results
            
        except Exception as e:
            print(f"WebSearchTool search error: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _trafilatura_extract(self, url: str) -> Optional[str]:
        try:
            downloaded = fetch_url(url)
            content = extract(downloaded)
            print(content)
            return content
        except Exception as e:
            print(f"WebSearchTool trafilatura extract error: {e}")
            return None

if __name__ == "__main__":
    url = "https://www.sohu.com/a/924444987_121991261"
    db_interface = RedisClient()
    llm_api_interface = OpenAIInterface()
    llm_summarizer = LLMFilterSummary(llm_api_interface)
    tool = WebSearchTool(db_interface, llm_summarizer)
    content = tool._trafilatura_extract(url)
    print(content)