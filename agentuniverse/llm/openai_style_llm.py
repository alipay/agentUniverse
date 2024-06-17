# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/5/21 13:52
# @Author  : weizjajj
# @Email   : weizhongjie.wzj@antgroup.com
# @FileName: openai_style_llm.py

from typing import Any, Optional, AsyncIterator, Iterator, Union

import httpx
import openai
import tiktoken
from langchain_core.language_models.base import BaseLanguageModel
from openai import OpenAI, AsyncOpenAI

from agentuniverse.llm.llm import LLM, LLMOutput
from agentuniverse.llm.openai_style_langchain_instance import LangchainOpenAIStyleInstance


class OpenAIStyleLLM(LLM):
    """This is a wrapper around the OpenAI API that implements a chat interface for the LLM.

    It uses the `chat` endpoint of the OpenAI API.
    It also supports using the `completion` endpoint instead of the `chat` endpoint.
    It supports both sync and async modes.

    Attributes:
        api_key (Optional[str]): The API key to use for authentication.
        organization (Optional[str]): The organization ID to use for authentication.
        api_base (Optional[str]): The base URL to use for the API requests.
        proxy (Optional[str]): The proxy to use for the API requests.
        client_args (Optional[dict]): Additional arguments to pass to the client.
    """

    api_key: Optional[str] = None
    organization: Optional[str] = None
    api_base: Optional[str] = None
    proxy: Optional[str] = None
    client_args: Optional[dict] = None

    def _new_client(self):
        """Initialize the openai client."""
        return OpenAI(
            api_key=self.api_key,
            organization=self.organization,
            base_url=self.api_base,
            timeout=self.request_timeout,
            max_retries=self.max_retries,
            http_client=httpx.Client(proxy=self.openai_proxy) if self.proxy else None,
            **(self.client_args or {}),
        )

    def _new_async_client(self):
        """Initialize the openai async client."""
        return AsyncOpenAI(
            api_key=self.api_key,
            organization=self.organization,
            base_url=self.api_base,
            timeout=self.request_timeout,
            max_retries=self.max_retries,
            http_client=httpx.AsyncClient(proxy=self.proxy) if self.proxy else None,
            **(self.client_args or {}),
        )

    def call(self, messages: list, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        """Run the OpenAI LLM.

        Args:
            messages (list): The messages to send to the LLM.
            **kwargs: Arbitrary keyword arguments.
        """
        streaming = kwargs.pop("streaming") if "streaming" in kwargs else self.streaming
        if 'stream' in kwargs:
            streaming = kwargs.pop('stream')
        self.client = self._new_client()
        client = self.client
        chat_completion = client.chat.completions.create(
            messages=messages,
            model=kwargs.pop('model', self.model_name),
            temperature=kwargs.pop('temperature', self.temperature),
            stream=kwargs.pop('stream', streaming),
            max_tokens=kwargs.pop('max_tokens', self.max_tokens),
            **kwargs,
        )
        if not streaming:
            text = chat_completion.choices[0].message.content
            self.close()
            return LLMOutput(text=text, raw=chat_completion.model_dump())
        return self.generate_stream_result(chat_completion)

    async def acall(self, messages: list, **kwargs: Any) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        """Asynchronously run the OpenAI LLM.

        Args:
            messages (list): The messages to send to the LLM.
            **kwargs: Arbitrary keyword arguments.
        """
        streaming = kwargs.pop("streaming") if "streaming" in kwargs else self.streaming
        self.async_client = self._new_async_client()
        async_client = self.async_client
        chat_completion = await async_client.chat.completions.create(
            messages=messages,
            model=kwargs.pop('model', self.model_name),
            temperature=kwargs.pop('temperature', self.temperature),
            stream=kwargs.pop('stream', streaming),
            max_tokens=kwargs.pop('max_tokens', self.max_tokens),
            **kwargs,
        )
        if not streaming:
            text = chat_completion.choices[0].message.content
            await self.aclose()
            return LLMOutput(text=text, raw=chat_completion.model_dump())
        return self.agenerate_stream_result(chat_completion)

    def as_langchain(self) -> BaseLanguageModel:
        """Convert the AgentUniverse(AU) openai llm class to the langchain openai llm class."""
        return LangchainOpenAIStyleInstance(self)

    def set_by_agent_model(self, **kwargs) -> None:
        """ Assign values of parameters to the OpenAILLM model in the agent configuration."""
        super().set_by_agent_model(**kwargs)
        if 'api_key' in kwargs and kwargs['api_key']:
            self.api_key = kwargs['api_key']
        if 'api_base' in kwargs and kwargs['api_base']:
            self.api_base = kwargs['api_base']
        if 'proxy' in kwargs and kwargs['proxy']:
            self.proxy = kwargs['proxy']
        if 'client_args' in kwargs and kwargs['client_args']:
            self.client_args = kwargs['client_args']

    @staticmethod
    def parse_result(chunk):
        """Generate the result of the stream."""
        chat_completion = chunk
        if not isinstance(chunk, dict):
            chunk = chunk.dict()
        if len(chunk["choices"]) == 0:
            return
        choice = chunk["choices"][0]
        message = choice.get("delta")
        text = message.get("content")
        if not text:
            return
        return LLMOutput(text=text, raw=chat_completion.model_dump())

    def generate_stream_result(self, stream: openai.Stream):
        """Generate the result of the stream."""
        for chunk in stream:
            llm_output = self.parse_result(chunk)
            if llm_output:
                yield llm_output
        self.close()

    async def agenerate_stream_result(self, stream: AsyncIterator) -> AsyncIterator[LLMOutput]:
        """Generate the result of the stream."""
        async for chunk in stream:
            llm_output = self.parse_result(chunk)
            if llm_output:
                yield llm_output

        await self.aclose()

    def get_num_tokens(self, text: str) -> int:
        """Get the number of tokens present in the text.

        Useful for checking if an input will fit in an openai model's context window.

        Args:
            text: The string input to tokenize.

        Returns:
            The integer number of tokens in the text.
        """
        try:
            encoding = tiktoken.encoding_for_model(self.model_name)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))

    def close(self):
        """Close the client."""
        if hasattr(self, 'client') and self.client:
            self.client.close()

    async def aclose(self):
        """Async close the client."""
        if hasattr(self, 'async_client') and self.async_client:
            await self.async_client.close()
