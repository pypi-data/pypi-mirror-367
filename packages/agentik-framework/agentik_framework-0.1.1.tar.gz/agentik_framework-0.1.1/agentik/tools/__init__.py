# agentik/tools/__init__.py

"""
Dynamic tool importer for agentik.tools package.

Scans the tools directory for modules containing classes that inherit from Tool,
registers them in `tool_registry` for dynamic usage.
"""

import os
import importlib
import inspect
from pathlib import Path
from agentik.tools.base import Tool

# Registry of all available tool classes
tool_registry = {}

def import_all_tools():
    """
    Dynamically import all tool modules and populate tool_registry.
    """
    tools_dir = Path(__file__).parent
    for file in os.listdir(tools_dir):
        if file.endswith(".py") and file not in ("__init__.py", "base.py"):
            module_name = f"agentik.tools.{file[:-3]}"
            try:
                module = importlib.import_module(module_name)
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and issubclass(obj, Tool) and obj is not Tool:
                        tool_registry[obj.name.lower()] = obj
            except Exception as e:
                print(f"[Warning] Failed to import {module_name}: {e}")

# Import all tools on module load
import_all_tools()
