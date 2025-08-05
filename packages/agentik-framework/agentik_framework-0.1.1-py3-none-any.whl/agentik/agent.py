# agentik/agent.py

"""
Agent module for Agentik.

This module defines the Agent class, which implements a simple reasoning loop:
plan → act → reflect. It allows the agent to process a prompt, decide an action
using an LLM, execute a tool, and store results in memory.
"""

from typing import List, Optional, Any
from agentik.utils import get_logger

# Initialize module-level logger
logger = get_logger(__name__)


class Agent:
    """
    The core Agent class for Agentik.

    Implements the standard agent reasoning loop:
    1. Plan: Use LLM to decide next action
    2. Act: Use tools to perform actions
    3. Reflect: Update memory with results
    """

    def __init__(self, name: str, goal: str, llm: Any, tools: List[Any], memory: Optional[Any] = None):
        """
        Initialize the Agent.

        Args:
            name (str): The name of the agent.
            goal (str): The agent's main goal or purpose.
            llm (LLMBase): A language model interface used for planning.
            tools (List[Tool]): List of available tools the agent can use.
            memory (MemoryBase, optional): Memory backend (in-memory or persistent).
        """
        self.name = name
        self.goal = goal
        self.llm = llm
        self.tools = tools or []
        self.memory = memory

    def plan(self, prompt: str) -> str:
        """
        Use the LLM backend to generate the next action.

        Args:
            prompt (str): Context or query passed to the LLM.

        Returns:
            str: LLM-generated action or response.
        """
        logger.info(f"[Plan] Using LLM to plan next step for: {prompt}")
        return self.llm.generate(prompt)

    def act(self, action: str) -> str:
        """
        Match the action to an available tool and run it.

        Args:
            action (str): The action string containing tool name and parameters.

        Returns:
            str: Result from the executed tool or fallback message.
        """
        logger.info(f"[Act] Executing action: {action}")
        for tool in self.tools:
            if tool.name.lower() in action.lower():
                return tool.run(action)

        return f"[Agent] No tool matched the action: {action}"

    def reflect(self, result: str):
        """
        Store the result in memory (if memory is enabled).

        Args:
            result (str): The outcome of the tool/action execution.
        """
        logger.info(f"[Reflect] Result: {result}")
        if self.memory:
            self.memory.remember(result)

    def run(self, prompt: str):
        """
        Execute the full reasoning loop: plan → act → reflect (up to 3 cycles).

        Args:
            prompt (str): The initial user query or task.
        """
        logger.info(f"\nAgent '{self.name}' starting with goal: {self.goal}\n")
        context = prompt

        for step in range(3):  # Limit to 3 steps
            logger.info(f"[Cycle {step+1}]")
            action = self.plan(context)
            result = self.act(action)
            self.reflect(result)

            # Exit early if LLM signals completion
            if "done" in action.lower() or "exit" in action.lower():
                logger.info("[Agent] Finished early.")
                break

            context = result
