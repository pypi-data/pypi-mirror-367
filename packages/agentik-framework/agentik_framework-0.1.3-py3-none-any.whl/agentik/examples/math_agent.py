"""
Math Agent
----------
Performs complex mathematical calculations using OpenRouter-powered LLM.
"""

from agentik.agent import Agent
from agentik.llms import DeepSeekModel
from agentik.memory import DictMemory
from agentik.tools.calculator import CalculatorTool
import os

if __name__ == "__main__":
    # Get API key securely from environment
    api_key = os.getenv("OPENROUTER_API_KEY", "")

    # Initialize LLM via OpenRouter
    llm = DeepSeekModel(
        api_key=api_key,
        model="deepseek/deepseek-chat-v3-0324:free"
    )

    # Configure the agent
    agent = Agent(
        name="MathAgent",
        goal="Perform complex calculations",
        llm=llm,
        tools=[CalculatorTool()],
        memory=DictMemory()  # In-memory storage
    )

    # Run the math task
    agent.run("Calculate 150 * (32 / 8)")
