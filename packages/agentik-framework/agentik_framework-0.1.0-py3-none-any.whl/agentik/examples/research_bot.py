"""
Research Bot
------------
Searches for and summarizes recent AI tools using OpenRouter and external tools.
"""

from agentik.agent import Agent
from agentik.llms import OpenRouterModel
from agentik.memory import JSONMemoryStore
from agentik.tools.websearch import WebSearchTool
from agentik.tools.calculator import CalculatorTool
from agentik.llms import DeepSeekModel
import os

if __name__ == "__main__":
    # Secure API key loading
    api_key = os.getenv("OPENROUTER_API_KEY", "")

    # Initialize LLM using OpenRouter
    llm = DeepSeekModel(
        api_key=api_key,
        model="deepseek/deepseek-chat-v3-0324:free"
    )

    # Create the agent
    agent = Agent(
        name="ResearchBot",
        goal="Summarize recent AI tools",
        llm=llm,
        tools=[WebSearchTool(), CalculatorTool()],
        memory=JSONMemoryStore("memory.json")
    )

    # Execute research task
    agent.run("Find the latest AI agent frameworks and summarize them.")
