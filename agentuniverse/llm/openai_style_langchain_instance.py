# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/5/21 13:52
# @Author  : weizjajj
# @Email   : weizhongjie.wzj@antgroup.com
# @FileName: langchain_openai_style_instance.py

from typing import Any, List, Optional, AsyncIterator, Iterator

from langchain.callbacks.manager import AsyncCallbackManagerForLLMRun, CallbackManagerForLLMRun
from langchain.schema import BaseMessage, ChatResult
from langchain_community.chat_models.openai import _convert_delta_to_message_chunk, _create_retry_decorator
from langchain_community.utils.openai import is_openai_v1
from langchain_core.language_models.chat_models import generate_from_stream, agenerate_from_stream
from langchain_core.messages import AIMessageChunk, get_buffer_string
from langchain_core.outputs import ChatGenerationChunk
from langchain_community.chat_models import ChatOpenAI

from agentuniverse.llm.llm import LLM


async def acompletion_with_retry(
        llm: ChatOpenAI,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
) -> Any:
    """Use tenacity to retry the async completion call."""
    if is_openai_v1():
        return await llm.llm.acall(**kwargs)

    retry_decorator = _create_retry_decorator(llm, run_manager=run_manager)

    @retry_decorator
    async def _completion_with_retry(**kwargs: Any) -> Any:
        # Use OpenAI's async api https://github.com/openai/openai-python#async-api
        return await llm.llm.acall(**kwargs)

    return await _completion_with_retry(**kwargs)


class LangchainOpenAIStyleInstance(ChatOpenAI):
    """Langchain OpenAI LLM wrapper."""

    llm: Optional[LLM] = None

    def __init__(self, llm: LLM):
        """The __init__ method.

        The agentUniverse LLM instance is passed to this class as an argument.
        Convert the attributes of agentUniverse(aU) LLM instance to the LangchainOpenAI object for initialization

        Args:
            llm (LLM): the agentUniverse(aU) LLM instance.
        """
        init_params = dict()
        init_params['model_name'] = llm.model_name if llm.model_name else 'gpt-3.5-turbo'
        init_params['temperature'] = llm.temperature if llm.temperature else 0.7
        init_params['request_timeout'] = llm.request_timeout
        init_params['max_tokens'] = llm.max_tokens
        init_params['max_retries'] = llm.max_retries if llm.max_retries else 2
        init_params['streaming'] = llm.streaming if llm.streaming else False
        init_params['openai_api_key'] = llm.api_key if llm.api_key else 'blank'
        init_params['openai_organization'] = llm.organization
        init_params['openai_api_base'] = llm.api_base
        init_params['openai_proxy'] = llm.proxy
        super().__init__(**init_params)
        self.llm = llm

    def _generate(
            self,
            messages: List[BaseMessage],
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            stream: Optional[bool] = None,
            **kwargs,
    ) -> ChatResult:
        """Run the Langchain OpenAI LLM."""
        should_stream = stream if stream is not None else self.streaming
        message_dicts, params = self._create_message_dicts(messages, stop)
        params = {**params, **kwargs}
        llm_output = self.llm.call(messages=message_dicts, **params)
        if not should_stream:
            return self._create_chat_result(llm_output.raw)
        stream_iter = self.as_langchain_chunk(llm_output)
        return generate_from_stream(stream_iter)

    async def _agenerate(
            self,
            messages: List[BaseMessage],
            stop: Optional[List[str]] = None,
            run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
            stream: Optional[bool] = None,
            **kwargs: Any,
    ) -> ChatResult:

        """Asynchronously run the Langchain OpenAI LLM."""
        should_stream = stream if stream is not None else self.streaming
        message_dicts, params = self._create_message_dicts(messages, stop)
        params = {**params, **kwargs}
        llm_output = await self.llm.acall(messages=message_dicts, **params)
        if not should_stream:
            return self._create_chat_result(llm_output.raw)
        stream_iter = self.as_langchain_achunk(llm_output)
        return await agenerate_from_stream(stream_iter)

    @staticmethod
    def as_langchain_chunk(stream, run_manager=None):
        default_chunk_class = AIMessageChunk
        for llm_result in stream:
            chunk = llm_result.raw
            if not isinstance(chunk, dict):
                chunk = chunk.dict()
            if len(chunk["choices"]) == 0:
                continue
            choice = chunk["choices"][0]
            chunk = _convert_delta_to_message_chunk(
                choice["delta"], default_chunk_class
            )
            finish_reason = choice.get("finish_reason")
            generation_info = (
                dict(finish_reason=finish_reason) if finish_reason is not None else None
            )
            default_chunk_class = chunk.__class__
            chunk = ChatGenerationChunk(message=chunk, generation_info=generation_info)
            yield chunk
            if run_manager:
                run_manager.on_llm_new_token(chunk.text, chunk=chunk)

    @staticmethod
    async def as_langchain_achunk(stream_iterator: AsyncIterator, run_manager=None) \
            -> AsyncIterator[ChatGenerationChunk]:
        default_chunk_class = AIMessageChunk
        async for llm_result in stream_iterator:
            chunk = llm_result.raw
            if not isinstance(chunk, dict):
                chunk = chunk.dict()
            if len(chunk["choices"]) == 0:
                continue
            choice = chunk["choices"][0]
            chunk = _convert_delta_to_message_chunk(
                choice["delta"], default_chunk_class
            )
            finish_reason = choice.get("finish_reason")
            generation_info = (
                dict(finish_reason=finish_reason) if finish_reason is not None else None
            )
            default_chunk_class = chunk.__class__
            chunk = ChatGenerationChunk(message=chunk, generation_info=generation_info)
            yield chunk
            if run_manager:
                await run_manager.on_llm_new_token(token=chunk.text, chunk=chunk)

    def get_num_tokens_from_messages(self, messages: List[BaseMessage]) -> int:
        messages_str = get_buffer_string(messages)
        return self.llm.get_num_tokens(messages_str)

    def completion_with_retry(
            self, run_manager: Optional[CallbackManagerForLLMRun] = None, **kwargs: Any
    ) -> Any:
        """Use tenacity to retry the completion call."""
        if is_openai_v1():
            return self.llm.call(**kwargs)

        retry_decorator = _create_retry_decorator(self, run_manager=run_manager)

        @retry_decorator
        def _completion_with_retry(**kwargs: Any) -> Any:
            return self.llm.call(**kwargs)

        return _completion_with_retry(**kwargs)

    def _stream(
            self,
            messages: List[BaseMessage],
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        message_dicts, params = self._create_message_dicts(messages, stop)
        params = {**params, **kwargs, "stream": True}

        default_chunk_class = AIMessageChunk
        for chunk in self.completion_with_retry(
                messages=message_dicts, run_manager=run_manager, **params
        ):
            chunk = chunk.raw
            if not isinstance(chunk, dict):
                chunk = chunk.dict()
            if len(chunk["choices"]) == 0:
                continue
            choice = chunk["choices"][0]
            chunk = _convert_delta_to_message_chunk(
                choice["delta"], default_chunk_class
            )
            finish_reason = choice.get("finish_reason")
            generation_info = (
                dict(finish_reason=finish_reason) if finish_reason is not None else None
            )
            default_chunk_class = chunk.__class__
            cg_chunk = ChatGenerationChunk(
                message=chunk, generation_info=generation_info
            )
            if run_manager:
                run_manager.on_llm_new_token(cg_chunk.text, chunk=cg_chunk)
            yield cg_chunk

    async def _astream(
            self,
            messages: List[BaseMessage],
            stop: Optional[List[str]] = None,
            run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> AsyncIterator[ChatGenerationChunk]:
        message_dicts, params = self._create_message_dicts(messages, stop)
        params = {**params, **kwargs, "stream": True}

        default_chunk_class = AIMessageChunk
        async for chunk in await acompletion_with_retry(
                self, messages=message_dicts, run_manager=run_manager, **params
        ):
            chunk = chunk.raw
            if not isinstance(chunk, dict):
                chunk = chunk.dict()
            if len(chunk["choices"]) == 0:
                continue
            choice = chunk["choices"][0]
            chunk = _convert_delta_to_message_chunk(
                choice["delta"], default_chunk_class
            )
            finish_reason = choice.get("finish_reason")
            generation_info = (
                dict(finish_reason=finish_reason) if finish_reason is not None else None
            )
            default_chunk_class = chunk.__class__
            cg_chunk = ChatGenerationChunk(
                message=chunk, generation_info=generation_info
            )
            if run_manager:
                await run_manager.on_llm_new_token(token=cg_chunk.text, chunk=cg_chunk)
            yield cg_chunk
