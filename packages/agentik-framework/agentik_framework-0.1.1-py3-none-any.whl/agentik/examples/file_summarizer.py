"""
File Summarizer Agent
----------------------
Reads a file and summarizes its content using an LLM via OpenRouter.
"""

from agentik.agent import Agent
from agentik.llms import DeepSeekModel
from agentik.memory import JSONMemoryStore
from agentik.tools.filereader import FileReaderTool
import os

if __name__ == "__main__":
    # Get API key from environment variable for security
    api_key = os.getenv("OPENROUTER_API_KEY", "")

    # Initialize DeepSeek model via OpenRouter
    llm = DeepSeekModel(
        api_key=api_key,
        model="deepseek/deepseek-chat-v3-0324:free"
    )

    # Initialize the file reader tool
    file_reader = FileReaderTool()

    # Read file content using tool
    file_path = "examples/sample.txt"
    tool_command = f"FileReaderTool {file_path}"
    file_content = file_reader.run(tool_command)

    # Set up the agent
    agent = Agent(
        name="FileSummarizer",
        goal="Read and summarize files",
        llm=llm,
        tools=[file_reader],
        memory=JSONMemoryStore("file_memory.json")
    )

    # Execute the agent with file content
    agent.run(file_content)
