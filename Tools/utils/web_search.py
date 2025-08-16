# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from ddgs import DDGS
import requests
import json

from Interfaces.llm_api_interface import OpenAIInterface
from Tools.utils.base_tool import BaseTool
from Data.mcp_models import MCP, ExecutableCommand
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

    def execute(self, mcp: MCP, executable_command: ExecutableCommand, **kwargs) -> dict:
        try:
            keywords = executable_command.params.get("keywords")
            num_results = executable_command.params.get("num_results", 3)
            
            # 验证参数
            if not keywords:
                print("WebSearchTool: No keywords provided")
                return {"error": "No keywords provided"}
            
            if not isinstance(keywords, list):
                print(f"WebSearchTool: Keywords must be a list, got {type(keywords)}")
                return {"error": f"Invalid keywords type: {type(keywords)}"}
            
            # 1. 执行搜索并获取原始内容
            content_results = self._search_and_extract(keywords, num_results)
            
            if not content_results:
                return {"error": "No search results found"}
            
            # 将所有内容结果合并为一个字符串
            raw_data_str = json.dumps(content_results, indent=2, ensure_ascii=False)

            # 2. 生成唯一的 Redis 键
            data_key = f"{mcp.session_id}:{mcp.global_cycle_count}:{self.tool_id}:{self.instance_id}"
            
            # 3. 将原始数据存入 Redis
            self.db_interface.store_data(data_key, content_results)
            
            # 4. 调用 LLMFilterSummary 生成摘要
            summary = self.llm_summarizer.process(mcp, raw_data=raw_data_str)
            
            # 5. 返回摘要和数据键给 Executor
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
            # 确保 keywords 是列表
            if not isinstance(keywords, list):
                print(f"WebSearchTool: Keywords must be a list, got {type(keywords)}")
                return []
            
            query = " ".join(str(k) for k in keywords if k)  # 安全地连接
            results = []
            
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
                        
                        # 安全地获取文本
                        text_content = soup.get_text(separator=" ", strip=True)
                        if text_content:
                            # 安全地分割和连接
                            text_parts = text_content.split()
                            if text_parts:
                                text = " ".join(text_parts)
                            else:
                                text = "No content extracted"
                        else:
                            text = "No content extracted"
                        
                        results.append({"url": url, "content": text})
                        
                    except Exception as e:
                        print(f"WebSearchTool: Failed to process {url}: {e}")
                        results.append({"url": url, "content": f"Error: {str(e)}"})
            
            return results
            
        except Exception as e:
            print(f"WebSearchTool search error: {e}")
            import traceback
            traceback.print_exc()
            return []
    