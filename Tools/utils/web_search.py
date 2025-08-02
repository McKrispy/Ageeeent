from bs4 import BeautifulSoup
from ddgs import DDGS
from dotenv import load_dotenv
from openai import OpenAI

import requests
import os
import json

class SearchEngine:
    def __init__(self, keywords, num_results=5):
        self.keywords = keywords
        self.num_results = num_results
        load_dotenv()
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(base_url="https://api.vveai.com/v1", api_key=self.api_key)
        self.html_results = []
        self.content_results = []
        self.summary_results = []

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
            except Exception as e:
                print(f"Error parsing content from {url}: {e}")
        self.content_results = content_results
        return content_results

    def duckSummary(self):
        if not self.api_key:
            raise ValueError("API key not set. Please set it via constructor.")

        summary_results = []

        for page in self.content_results:
            url = page["url"]
            content = page["content"][:4000] # Token limit

            prompt = f"Please summarize the following content in 100 words: \n\n{content}\n\nSummary:"

            try:
                response = self.client.chat.completions.create(model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300)

                summary = response.choices[0].message.content
                summary_results.append({
                    "url": url,
                    "summary": summary
                })

            except Exception as e:
                print(f"Error summarizing content from {url}: {e}")
        self.summary_results = summary_results

        base_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(base_dir, "temp_output")
        output_file = os.path.join(output_dir, "web_search_results.json")
        if not os.path.exists(output_dir):
            print(f"\nDirectory {output_dir} does not exist. Creating...")
            os.makedirs(output_dir)
        else:
            print(f"\nDirectory {output_dir} already exists.")

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(summary_results, f, ensure_ascii=False, indent=2)

        print(f"\nSummary saved to: {output_file}")
        return summary_results

if __name__ == "__main__":
    search_engine = SearchEngine(["python", "programming"])
    search_engine.duckSearch()
    search_engine.duckContent()
    search_engine.duckSummary()
    print(search_engine.summary_results)