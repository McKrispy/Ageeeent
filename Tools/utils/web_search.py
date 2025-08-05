from bs4 import BeautifulSoup
from ddgs import DDGS
from Tools.utils.base_tool import BaseTool

import requests

class WebSearchTool(BaseTool):
    def __init__(self, keywords, num_results=5):
        self.keywords = keywords
        self.num_results = num_results
        self.html_results = []
        self.content_results = []

    def execute(self, **kwargs):
        self.duckSearch()
        self.duckContent()
        print(f"WebSearchTool Output: {self.content_results}")
        return self.content_results

    def duckSearch(self):
        query = " ".join(self.keywords)
        html_results = []

        with DDGS() as ddgs:
            for result in ddgs.text(query, max_results=self.num_results):
                url = result.get("href")
                try:
                    response = requests.get(url, timeout=5, headers={
                        "User-Agent": "Mozilla/5.0"
                    })
                    html_results.append({
                        "url": url,
                        "html": response.text
                    })
                except Exception as e:
                    print(f"Failed to fetch {url}: {e}")
        self.html_results = html_results
        
        return html_results

    def duckContent(self):
        content_results = []
        for item in self.html_results:
            url = item["url"]
            html = item["html"]
            try:
                soup = BeautifulSoup(html, "html.parser")

                for tag in soup(["script", "style", "button", "nav", "footer", "form", "aside"]):
                    tag.decompose()

                text = soup.get_text(separator=" ", strip=True)
                clean_text = ' '.join(text.split())

                content_results.append({
                    "url": url,
                    "content": clean_text
                })
                # TODO: Ready to connect to redis
            except Exception as e:
                print(f"Error parsing content from {url}: {e}")
        self.content_results = content_results
        return content_results

if __name__ == "__main__":
    web_search_tool = WebSearchTool(["python", "programming"])
    web_search_tool.duckSearch()
    web_search_tool.duckContent()