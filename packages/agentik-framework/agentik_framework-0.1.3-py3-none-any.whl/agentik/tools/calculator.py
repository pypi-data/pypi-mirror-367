# agentik/tools/calculator.py

"""
Tool: CalculatorTool
Safely evaluates basic math expressions using Python's eval and the math module.
"""

import math
from agentik.tools.base import Tool

class CalculatorTool(Tool):
    name = "calculator"
    description = "Evaluate basic math expressions safely."

    def run(self, input_text: str) -> str:
        """
        Evaluate a math expression passed after the 'calculator' keyword.
        Supports basic operations and math module functions.
        """
        try:
            expression = input_text.replace(self.name, "", 1).strip()
            result = eval(expression, {"__builtins__": None, "math": math})
            return f"Result: {result}"
        except Exception as e:
            return f"[CalculatorTool Error]: {str(e)}"
