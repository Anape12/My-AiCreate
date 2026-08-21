import requests

from .tool import Tool


class WebSearchTool(Tool):
    name = "web_search"
    description = "Searches the web for current, public information."
    requires_online = True

    def __init__(self, sourced_memory=None):
        self.sourced_memory = sourced_memory

    def execute(self, input: str) -> str:
        response = requests.get(
            "https://api.duckduckgo.com/",
            params={"q": input, "format": "json", "no_html": "1", "skip_disambig": "1"},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        snippets = [data.get("AbstractText", "")]
        for topic in data.get("RelatedTopics", []):
            if isinstance(topic, dict) and topic.get("Text"):
                snippets.append(topic["Text"])
            if len([item for item in snippets if item]) >= 3:
                break
        result = "\n".join(item for item in snippets if item)
        url = data.get("AbstractURL", "")
        if result and self.sourced_memory:
            self.sourced_memory.add(result, source="DuckDuckGo Instant Answer", query=input, url=url)
        return result or "No concise web search result was found."
