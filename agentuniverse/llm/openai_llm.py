# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/4/2 16:15
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: openai_llm.py
from typing import Any, Optional

from langchain_core.language_models.base import BaseLanguageModel
from openai import OpenAI, AsyncOpenAI
from pydantic import Field

from agentuniverse.llm.langchain_instance import LangchainOpenAI
from agentuniverse.llm.llm import LLM, LLMOutput
from agentuniverse.base.util.env_util import get_from_env


class OpenAILLM(LLM):
    """The openai llm class.

    Attributes:
        openai_api_key (Optional[str], optional): The API key for the OpenAI API.
        This automatically infers the `openai_api_key` from the environment variable `OPENAI_API_KEY` if not provided.

        openai_organization (Optional[str], optional): The OpenAI organization.
        This automatically infers the `openai_organization` from the environment variable `OPENAI_ORGANIZATION` if not provided.

        openai_api_base (Optional[str], optional): The OpenAI base url.
        This automatically infers the `openai_api_base` from the environment variable `OPENAI_API_BASE` if not provided.

        openai_client_args (Optional[dict], optional): Additional arguments to pass to the OpenAI client.
   """

    openai_api_key: Optional[str] = Field(default_factory=lambda: get_from_env("OPENAI_API_KEY"))
    openai_organization: Optional[str] = Field(default_factory=lambda: get_from_env("OPENAI_ORGANIZATION"))
    openai_api_base: Optional[str] = Field(default_factory=lambda: get_from_env("OPENAI_API_BASE"))
    openai_client_args: Optional[dict] = None

    def _new_client(self):
        """Initialize the openai client."""
        return OpenAI(
            api_key=self.openai_api_key,
            organization=self.openai_organization,
            base_url=self.openai_api_base,
            timeout=self.request_timeout,
            max_retries=self.max_retries,
            **(self.openai_client_args or {}),
        )

    def _new_async_client(self):
        """Initialize the openai async client."""
        return AsyncOpenAI(
            api_key=self.openai_api_key,
            organization=self.openai_organization,
            base_url=self.openai_api_base,
            timeout=self.request_timeout,
            max_retries=self.max_retries,
            **(self.openai_client_args or {}),
        )

    def call(self, messages: list, **kwargs: Any) -> LLMOutput:
        """Run the OpenAI LLM.

        Args:
            messages (list): The messages to send to the LLM.
            **kwargs: Arbitrary keyword arguments.
        """
        if self.client is None:
            self.client = self._new_client()
        chat_completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            max_tokens=self.max_tokens,
            stream=self.streaming,
            **kwargs,
        )
        text = chat_completion.choices[0].message.content
        return LLMOutput(text=text)

    async def acall(self, messages: list, **kwargs: Any) -> LLMOutput:
        """Asynchronously run the OpenAI LLM.

        Args:
            messages (list): The messages to send to the LLM.
            **kwargs: Arbitrary keyword arguments.
        """

        if self.async_client is None:
            self.async_client = self._new_async_client()
        chat_completion = await self.async_client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            max_tokens=self.max_tokens,
            stream=self.streaming,
            **kwargs,
        )
        text = chat_completion.choices[0].message.content
        return LLMOutput(text=text)

    def as_langchain(self) -> BaseLanguageModel:
        """Convert the AgentUniverse openai llm class to the langchain openai llm class."""
        return LangchainOpenAI(self)

    def set_by_agent_model(self, **kwargs) -> None:
        """ Assign values of parameters to the OpenAILLM model in the agent configuration."""
        super().set_by_agent_model(**kwargs)
        if 'openai_api_key' in kwargs and kwargs['openai_api_key']:
            self.openai_api_key = kwargs['openai_api_key']
        if 'openai_api_base' in kwargs and kwargs['openai_api_base']:
            self.openai_api_base = kwargs['openai_api_base']
        if 'openai_client_args' in kwargs and kwargs['openai_client_args']:
            self.openai_client_args = kwargs['openai_client_args']
