# agentik/tools/template.py

"""
Tool: TemplateTool
Demonstrates how to create a custom tool with basic text processing logic.
"""

from agentik.tools.base import Tool

class TemplateTool(Tool):
    name = "template"
    description = "A template tool that demonstrates how to build a custom tool."

    def run(self, input_text: str) -> str:
        """
        Processes the string following 'template' and returns a formatted response.
        """
        command = input_text.replace(self.name, "", 1).strip()

        if not command:
            return f"[{self.name}] No input provided."

        return f"[{self.name}] Processed: {command}"
