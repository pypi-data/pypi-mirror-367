# agentik/config.py

"""
Configuration loader for the Agentik framework.

Parses YAML or JSON files to instantiate and return a fully configured Agent object.
Supports multiple LLMs, memory backends, and tool registration via dynamic registry.
"""

import yaml
import json
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, ValidationError

from agentik.agent import Agent
from agentik.llms import (
    OpenAIModel,
    ClaudeModel,
    MistralModel,
    DeepSeekModel,
    LocalLLM
)
from agentik.memory import DictMemory, JSONMemoryStore
from agentik.tools import tool_registry
from agentik.tools.base import Tool


# ----------------------- Config Models -----------------------

class LLMConfig(BaseModel):
    """
    LLM configuration schema loaded from YAML/JSON.

    Attributes:
        type (str): Type of LLM backend (e.g., openai, claude, mistral, local).
        api_key (Optional[str]): API key for hosted LLMs.
        model (Optional[str]): Model name (e.g., gpt-3.5-turbo).
        url (Optional[str]): URL for local/inference API.
    """
    type: str
    api_key: Optional[str] = None
    model: Optional[str] = None
    url: Optional[str] = None


class MemoryConfig(BaseModel):
    """
    Memory configuration schema.

    Attributes:
        type (str): Memory backend (dict or json).
        path (Optional[str]): Path to memory file (if using JSON).
    """
    type: str
    path: Optional[str] = "memory.json"


class AgentConfig(BaseModel):
    """
    Top-level Agent configuration schema.

    Attributes:
        name (str): Agent name.
        goal (str): Agent's main objective.
        llm (LLMConfig): LLM configuration block.
        tools (List[str]): List of tool names to use.
        memory (Optional[MemoryConfig]): Memory configuration block.
    """
    name: str
    goal: str
    llm: LLMConfig
    tools: List[str]
    memory: Optional[MemoryConfig]


# -------------------- Config Loader Function --------------------

def load_agent_config(path: str) -> Agent:
    """
    Load and validate an Agent configuration from a YAML or JSON file.

    Args:
        path (str): Path to the config file.

    Returns:
        Agent: A fully instantiated Agent object.

    Raises:
        FileNotFoundError: If config file does not exist.
        ValueError: If config is invalid or unsupported.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    # Parse raw YAML or JSON content
    if file_path.suffix in [".yaml", ".yml"]:
        with open(file_path, "r", encoding="utf-8") as f:
            raw_config = yaml.safe_load(f)
    elif file_path.suffix == ".json":
        with open(file_path, "r", encoding="utf-8") as f:
            raw_config = json.load(f)
    else:
        raise ValueError("Unsupported config format. Use .yaml/.yml or .json")

    # Validate using Pydantic schema
    try:
        cfg = AgentConfig(**raw_config)
    except ValidationError as e:
        raise ValueError(f"Invalid config: {e}")

    # Instantiate LLM backend
    llm_type = cfg.llm.type.lower()
    if llm_type == "openai":
        llm = OpenAIModel(api_key=cfg.llm.api_key, model=cfg.llm.model or "gpt-3.5-turbo")
    elif llm_type == "claude":
        llm = ClaudeModel(api_key=cfg.llm.api_key, model=cfg.llm.model)
    elif llm_type == "mistral":
        llm = MistralModel(api_key=cfg.llm.api_key, model=cfg.llm.model)
    elif llm_type == "deepseek":
        llm = DeepSeekModel(api_key=cfg.llm.api_key, model=cfg.llm.model)
    elif llm_type == "local":
        llm = LocalLLM(api_url=cfg.llm.url)
    else:
        raise ValueError(f"Unsupported LLM type: {cfg.llm.type}")

    # Instantiate memory backend
    memory = None
    if cfg.memory:
        mem_type = cfg.memory.type.lower()
        if mem_type == "dict":
            memory = DictMemory()
        elif mem_type == "json":
            memory = JSONMemoryStore(filepath=cfg.memory.path or "memory.json")
        else:
            raise ValueError(f"Unsupported memory type: {cfg.memory.type}")

    # Load and instantiate tools
    tools = []
    for tool_name in cfg.tools:
        tool_class = tool_registry.get(tool_name.lower())
        if tool_class:
            tools.append(tool_class())
        else:
            print(f"[Warning] Tool '{tool_name}' not found in registry. Skipping.")

    # Return configured Agent instance
    return Agent(
        name=cfg.name,
        goal=cfg.goal,
        llm=llm,
        tools=tools,
        memory=memory
    )
