# 🤖 Agentik – Modular Agentic AI Framework for Python

> A lightweight, modern, and pluggable Python framework to build AI agents with reasoning, memory, tool-use, and LLM backend support — designed to be minimal, extensible, and developer-friendly.

---

## 🔍 What is Agentik?

**Agentik** is a Python library that helps you build intelligent agents that can **reason**, **plan**, **act**, and **reflect** using any large language model (LLM) backend (e.g., OpenAI, Claude, Mistral via OpenRouter, or your local model). It abstracts the complexity and gives you:

- 🔌 LLM plugin support (OpenAI, Claude, etc.)
- 🧠 Memory integration (Dict, JSON, Vector optional)
- 🛠 Tool support (web search, calculator, file I/O)
- ⚙️ YAML or Python-based config
- 🖥 CLI for easy launching and debugging
- 🔒 API-key agnostic — the **user supplies their own keys**

---

## 🚀 Features

- Define agents in **Python or YAML**
- Core agent loop: `plan → act → reflect → iterate`
- Pluggable **tools and memory systems**
- Easily extend tools with Python
- Support for **streaming, retry, and debugging**
- CLI interface built with [Typer](https://typer.tiangolo.com/)
- Designed to be **lightweight**, **transparent**, and **powerful**

---

## 📁 Folder Structure

```
agentik/
│
├── agent.py          # 🧠 Core agent class and reasoning loop
├── llms.py           # 🔌 LLM backend interfaces (OpenAI, Claude, etc.)
├── tools/            # 🛠 Built-in and user-defined tools
│   └── __init__.py
│   └── calculator.py
│   └── websearch.py
│   └── filereader.py
│   └── ...
├── memory.py         # 🧠 Memory backends (Dict, JSON, FAISS, etc.)
├── config.py         # 🧾 YAML/JSON config parser using pydantic
├── cli.py            # 💻 CLI interface using Typer
├── utils.py          # ⚙️ Logger, token counter, helper functions
│
examples/             # 🎯 Sample agents and use-cases
tests/                # 🧪 Unit and integration tests
configs/              # ⚙️ YAML-based agent configuration files
```

---

## 🧠 Agent Workflow

The typical execution flow of an Agent in agentik:

```
[User Prompt] 
    ↓
[Agent.run(prompt)]
    ↓
[Plan Step] → Uses LLM to decide next action/tool
    ↓
[Act Step] → Runs selected tool or memory query
    ↓
[Reflect Step] → Evaluates outcome and updates memory
    ↓
[Repeat or Finish]
```

---

## 📦 Installation

> **Python 3.10+ is required**

```bash
pip install agentik-framework
```

---

## 🛠 Usage

### ✨ Create an Agent (Python Way)

```python
from agentik import Agent
from agentik.tools import WebSearchTool, CalculatorTool
from agentik.llms import OpenAIModel
from agentik.memory import JSONMemoryStore

agent = Agent(
    name="AIAssistant",
    goal="Find and summarize the latest AI trends.",
    tools=[WebSearchTool(), CalculatorTool()],
    llm=OpenAIModel(api_key="your-api-key-here", model="gpt-4"),
    memory=JSONMemoryStore("memory.json")
)

agent.run("What's the latest in AI agent frameworks?")
```

---

### ⚙️ Create an Agent via YAML (config.yaml)

```yaml
name: "ResearchBot"
goal: "Summarize recent advancements in generative AI"
llm:
  type: openai
  model: gpt-4
  api_key: "YOUR_KEY_HERE"
tools:
  - web_search
  - file_reader
memory:
  type: json
  path: "memory.json"
```

---

## 📂 Main File to Run

There are **two main entrypoints** to run the framework:

### 1. **Python File**
You can create and run a Python file such as `run_agent.py`:

```python
from agentik.config import load_agent_config
from agentik.agent import Agent

agent = load_agent_config("configs/my_agent.yaml")
agent.run("What are LLM agents?")
```

### 2. **CLI Command (Recommended)**

```bash
agentik run configs/my_agent.yaml --verbose
```

> Make sure you run this inside the directory containing your YAML and memory files.

---

## 🧠 Supported LLMs

agentik supports the following backends (via your API keys):

- OpenAI (via OpenRouter)
- Mistral (via OpenRouter)
- Claude (via OpenRouter)
- DeepSeek (via OpenRouter)
- Local models via REST API

All models are initialized via the `llms.py` interfaces and passed as parameters. No key is embedded in the code.

---

## 🔌 Built-in Tools

| Tool Name        | Description                                 |
|------------------|---------------------------------------------|
| `CalculatorTool` | Evaluate math expressions                   |
| `WebSearchTool`  | Search web results using DuckDuckGo/SerpAPI |
| `FileReaderTool` | Read content from .txt or .md files         |
| `JsonTool`       | Work with structured JSON documents         |

> Tools are extendable: just subclass `Tool` and implement a `run(input)` method.

---

## 📂 Where to Put Code?

| File                  | What to write here                                                |
|-----------------------|------------------------------------------------------------------|
| `agent.py`            | Core agent planning loop (already built-in)                      |
| `llms.py`             | Add your own LLM wrapper classes (if needed)                     |
| `memory.py`           | Custom memory strategies (default: Dict, JSON)                   |
| `tools/`              | Add new tools (e.g., `mytool.py`) and register dynamically       |
| `config.py`           | Modify or validate YAML loading logic (via `pydantic`)           |
| `cli.py`              | Main command-line logic (already pre-written via `typer`)        |
| `examples/`           | Place your sample agents or demo scripts                         |
| `configs/`            | Store reusable YAML configuration for agents                     |

---

## 🧪 Testing

```bash
pytest tests/
```

You can mock LLM API responses and test agent planning, memory storage, and tool execution.

---

## 🖥 CLI Commands

```bash
agentik run configs/my_agent.yaml
agentik list-tools
agentik create-agent
agentik explain memory
```

Flags:

- `--verbose` → detailed logs
- `--dry-run` → simulate without actual LLM/API calls

---

## 📚 Documentation

- Markdown-based, hosted on GitHub Pages
- Located in `docs/` (optional)
- Includes: Getting Started, API Reference, Tool Dev Guide

---

## 🧑‍💻 Contributing

We welcome contributions!

- Fork this repo
- Add your tool or feature
- Write tests in `tests/`
- Submit PR with clear explanation

---

## 📦 Packaging (for PyPI)

```bash
python -m build
twine upload dist/*
```

---

## 📄 License

MIT License © 2025 [Vinay Joshi, Avinash Raghuvanshi]

---

## 🧠 Philosophy

agentik isn’t trying to do everything for you — it gives you clean scaffolding and powerful abstractions to build your own intelligent agent workflows, **your way**.

Build smart. Stay lightweight. Go modular.

---

