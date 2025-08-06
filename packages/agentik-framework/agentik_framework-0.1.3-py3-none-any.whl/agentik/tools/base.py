# agentik/tools/base.py

"""
Abstract base class for all tools used in the Agentik framework.
Each tool must implement the `run()` method.
"""

class Tool:
    name: str = "BaseTool"
    description: str = "Base tool class"

    def run(self, input_text: str) -> str:
        """
        Main logic for tool execution. Must be overridden by child classes.
        """
        raise NotImplementedError("You must override the run() method.")

    def __repr__(self):
        return f"<Tool name={self.name}>"
