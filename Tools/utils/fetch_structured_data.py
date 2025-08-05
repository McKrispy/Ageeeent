from Tools.utils.base_tool import BaseTool

class Source:
    def __init__(self, name, api, type):
        self.name = name
        self.api = api
        self.type = type

    def use_api(self, keywords):
        structured_data = self.api(keywords)
        return structured_data

available_sources = [
    Source(name="Google", api="https://www.google.com", type="web"),
    Source(name="Bing", api="https://www.bing.com", type="web"),
    Source(name="DuckDuckGo", api="https://www.duckduckgo.com", type="web"),
    Source(name="Wikipedia", api="https://www.wikipedia.org", type="web"),
    Source(name="Twitter", url="https://www.twitter.com", type="social"),
]

class FetchStructuredDataTool(BaseTool):
    def __init__(self, llm, available_sources):
        self.llm = llm # TODO: Need to be configured to deal with the sources selection
        self.available_sources = available_sources
        self.structured_data = []

    def execute(self, **kwargs):
        keywords, intension = self.intensionRecognition(kwargs["query"])
        sources = self.sourceSelection(intension)
        structured_data = self.fetchData(keywords, sources)
        return structured_data
    
    def intensionRecognition(self, query):
        # TODO: Extract the intension from the query
        keywords, intension = self.llm(query)
        return keywords, intension
    
    def sourceSelection(self, intension):
        # TODO: Complete the logic of source selection
        sources = self.llm(intension, self.available_sources)
        return sources
    
    def fetchData(self, keywords, sources):
        # TODO: Complete the logic of data fetching
        for source in sources:
            data = source.use_api(keywords)
            self.structured_data.append(data)
        return self.structured_data
