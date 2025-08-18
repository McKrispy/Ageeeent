# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from ddgs import DDGS
import requests
import json
import time
import random
from typing import Optional

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
        
        # 配置重试参数
        self.max_retries = 3
        self.retry_delay = 2
        
        # 轮换User-Agent列表
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        ]

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
                    
                    content = self._fetch_url_with_retry(url)
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

    def _fetch_url_with_retry(self, url: str) -> Optional[str]:
        for attempt in range(self.max_retries):
            try:
                user_agent = random.choice(self.user_agents)
                headers = {
                    "User-Agent": user_agent,
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Accept-Encoding": "gzip, deflate",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                }
                
                print(f"WebSearchTool: Attempting to fetch {url} (attempt {attempt + 1}/{self.max_retries})")
                
                resp = requests.get(
                    url,
                    timeout=15,
                    headers=headers,
                    allow_redirects=True
                )
                
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, "html.parser")
                    text_content = soup.get_text(separator=" ", strip=True)
                    
                    if text_content:
                        text_parts = text_content.split()
                        if text_parts:
                            return " ".join(text_parts)
                        else:
                            return "No content extracted"
                    else:
                        return "No content extracted"
                
                elif resp.status_code in [404]:
                    print(f"WebSearchTool: Got status {resp.status_code} for {url}, abandoning URL")
                    return None
                
                elif resp.status_code in [403, 429, 500, 502, 503, 504]:
                    print(f"WebSearchTool: Got status {resp.status_code} for {url}, will retry...")
                    
                    if attempt < self.max_retries - 1:
                        delay = self.retry_delay + random.uniform(0, 2)
                        print(f"WebSearchTool: Waiting {delay:.2f} seconds before retry...")
                        time.sleep(delay)
                        continue
                    else:
                        print(f"WebSearchTool: Failed to fetch {url} after {self.max_retries} attempts")
                        return None 
                
                else:
                    print(f"WebSearchTool: Got non-retryable status {resp.status_code} for {url}, abandoning URL")
                    return None 
                    
            except requests.exceptions.Timeout:
                print(f"WebSearchTool: Timeout error for {url} (attempt {attempt + 1})")
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay + random.uniform(0, 1)
                    time.sleep(delay)
                    continue
                else:
                    print(f"WebSearchTool: Timeout error for {url} after all retries")
                    return None 
                    
            except requests.exceptions.ConnectionError:
                print(f"WebSearchTool: Connection error for {url} (attempt {attempt + 1})")
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay + random.uniform(0, 1)
                    time.sleep(delay)
                    continue
                else:
                    print(f"WebSearchTool: Connection error for {url} after all retries")
                    return None 
                    
            except Exception as e:
                print(f"WebSearchTool: Unexpected error for {url}: {e}")
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay + random.uniform(0, 1)
                    time.sleep(delay)
                    continue
                else:
                    print(f"WebSearchTool: Unexpected error for {url} after all retries")
                    return None 
        
        return None
