# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/14 16:07
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: chat_memory.py
from typing import Optional, List

from langchain.memory.chat_memory import BaseChatMemory

from agentuniverse.agent.memory.enum import MemoryTypeEnum
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.memory.message import Message
from agentuniverse.agent.memory.langchain_instance import AuConversationSummaryBufferMemory, \
    AuConversationTokenBufferMemory
from agentuniverse.base.config.component_configer.configers.memory_configer import MemoryConfiger
from agentuniverse.llm.llm import LLM


class ChatMemory(Memory):
    """The basic class for chat memory model.

    Attributes:
        llm (LLM): the LLM instance used by this memory.
        input_key (Optional[str]): The input key in the model input parameters is used to find the specific query in a
        round of conversations.
        output_key (Optional[str]): The output key in the model output parameters is used to find the specific result
        in a round of conversations.
        messages (Optional[List[Message]]): The list of conversation messages to send to the LLM memory.
    """

    llm: Optional[LLM] = None
    input_key: Optional[str] = None
    output_key: Optional[str] = None
    messages: Optional[List[Message]] = None
    prompt_version: Optional[str] = None

    def as_langchain(self) -> BaseChatMemory:
        """Convert the AgentUniverse(AU) chat memory class to the langchain chat memory class."""
        if self.llm is None:
            raise ValueError("Must set `llm` when using langchain memory.")
        if self.type is None or self.type == MemoryTypeEnum.SHORT_TERM:
            return AuConversationTokenBufferMemory(llm=self.llm.as_langchain(), memory_key=self.memory_key,
                                                   input_key=self.input_key, output_key=self.output_key,
                                                   max_token_limit=self.max_tokens, messages=self.messages)
        elif self.type == MemoryTypeEnum.LONG_TERM:
            return AuConversationSummaryBufferMemory(llm=self.llm.as_langchain(), memory_key=self.memory_key,
                                                     input_key=self.input_key, output_key=self.output_key,
                                                     max_token_limit=self.max_tokens, messages=self.messages,
                                                     prompt_version=self.prompt_version)

    def set_by_agent_model(self, **kwargs) -> None:
        """ Assign values of parameters to the ChatMemory model in the agent configuration."""
        super().set_by_agent_model(**kwargs)
        if 'messages' in kwargs and kwargs['messages']:
            self.messages = kwargs['messages']
        if 'llm' in kwargs and kwargs['llm']:
            self.llm = kwargs['llm']
        if 'input_key' in kwargs and kwargs['input_key']:
            self.input_key = kwargs['input_key']
        if 'output_key' in kwargs and kwargs['output_key']:
            self.output_key = kwargs['output_key']

    def initialize_by_component_configer(self, component_configer: MemoryConfiger) -> 'ChatMemory':
        """Initialize the chat memory by the ComponentConfiger object.
        Args:
            component_configer(MemoryConfiger): the ComponentConfiger object
        Returns:
            ChatMemory: the ChatMemory object
        """
        super().initialize_by_component_configer(component_configer)
        if component_configer.input_key:
            self.input_key = component_configer.input_key
        if component_configer.output_key:
            self.output_key = component_configer.output_key
        if component_configer.prompt_version:
            self.prompt_version = component_configer.prompt_version
        return self
