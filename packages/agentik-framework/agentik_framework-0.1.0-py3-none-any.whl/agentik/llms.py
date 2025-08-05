# agentik/llms.py

"""
Language Model (LLM) interfaces for the Agentik framework.

Provides unified abstractions for connecting to various LLM backends via OpenRouter
or local inference APIs. Each model implements the `LLMBase` interface.
"""

import abc
from typing import Optional
import requests
from openai import OpenAI


# ---------------------- Abstract Base Class ----------------------

class LLMBase(abc.ABC):
    """
    Abstract base class for all LLM backends.
    All LLM implementations must implement the `generate()` method.
    """

    @abc.abstractmethod
    def generate(self, prompt: str) -> str:
        """
        Generate a response for the given prompt.
        """
        pass


# ---------------------- OpenRouter-Based Models ----------------------

class OpenAIModel(LLMBase):
    """
    OpenAI GPT model served via OpenRouter.

    Default model: openai/gpt-4o
    """

    def __init__(self, api_key: str, site_url: str = "", site_name: str = "", model: str = "openai/gpt-4o"):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        self.headers = {
            "HTTP-Referer": site_url,
            "X-Title": site_name,
        }
        self.model = model

    def generate(self, prompt: str) -> str:
        """
        Generate a response using OpenAI model via OpenRouter.
        """
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                extra_headers=self.headers,
                extra_body={}
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"[OpenAIModel Error]: {str(e)}"


class ClaudeModel(LLMBase):
    """
    Claude LLM served via OpenRouter.

    Default model: anthropic/claude-sonnet-4
    """

    def __init__(self, api_key: str, site_url: str = "", site_name: str = "", model: str = "anthropic/claude-sonnet-4"):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        self.headers = {
            "HTTP-Referer": site_url,
            "X-Title": site_name,
        }
        self.model = model

    def generate(self, prompt: str) -> str:
        """
        Generate a response using Claude model via OpenRouter.
        """
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                extra_headers=self.headers,
                extra_body={}
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"[ClaudeModel Error]: {str(e)}"


class MistralModel(LLMBase):
    """
    Mistral LLM served via OpenRouter.

    Default model: mistralai/mistral-nemo:free
    """

    def __init__(self, api_key: str, site_url: str = "", site_name: str = "", model: str = "mistralai/mistral-nemo:free"):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        self.headers = {
            "HTTP-Referer": site_url,
            "X-Title": site_name,
        }
        self.model = model

    def generate(self, prompt: str) -> str:
        """
        Generate a response using Mistral model via OpenRouter.
        """
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                extra_headers=self.headers,
                extra_body={}
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"[MistralModel Error]: {str(e)}"


class DeepSeekModel(LLMBase):
    """
    DeepSeek LLM served via OpenRouter.

    Default model: deepseek/deepseek-chat-v3-0324:free
    """

    def __init__(self, api_key: str, site_url: str = "", site_name: str = "", model: str = "deepseek/deepseek-chat-v3-0324:free"):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        self.headers = {
            "HTTP-Referer": site_url,
            "X-Title": site_name,
        }
        self.model = model

    def generate(self, prompt: str) -> str:
        """
        Generate a response using DeepSeek model via OpenRouter.
        """
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                extra_headers=self.headers,
                extra_body={}
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"[DeepSeekModel Error]: {str(e)}"


# ---------------------- Local Model ----------------------

class LocalLLM(LLMBase):
    """
    Local LLM backend for self-hosted or offline inference APIs.

    Args:
        api_url (str): URL of the local inference API endpoint.
    """

    def __init__(self, api_url: str):
        self.api_url = api_url

    def generate(self, prompt: str) -> str:
        """
        Generate a response by sending a POST request to the local model server.

        Returns:
            str: The model's output or error message.
        """
        try:
            response = requests.post(self.api_url, json={"prompt": prompt})
            if response.status_code == 200:
                return response.json().get("output", "")
            return f"[LocalLLM Error] Status {response.status_code}"
        except Exception as e:
            return f"[LocalLLM Error]: {str(e)}"
