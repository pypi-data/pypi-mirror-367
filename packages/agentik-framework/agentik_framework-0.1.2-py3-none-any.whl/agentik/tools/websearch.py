# agentik/tools/websearch.py

"""
Tool: WebSearchTool
Fetches a short summary from DuckDuckGo Instant Answer API based on user query.
"""

import requests
from agentik.tools.base import Tool

class WebSearchTool(Tool):
    name = "websearch"
    description = "Perform a quick web search using DuckDuckGo."

    def run(self, input_text: str) -> str:
        """
        Extracts query from input and returns summary from DuckDuckGo API.
        """
        query = input_text.replace(self.name, "", 1).strip()
        if not query:
            return "[WebSearchTool] No query provided."

        url = f"https://api.duckduckgo.com/?q={query}&format=json"
        try:
            response = requests.get(url, timeout=5)
            data = response.json()
            return data.get("AbstractText") or "No summary available."
        except Exception as e:
            return f"[WebSearchTool Error]: {str(e)}"
