#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time   : 2024/7/29 10:32
# @Author : fluchw
# @Email  : zerozed00@qq.com
# @File   ：role_memory.py
from typing import Optional, List

from langchain.memory.chat_memory import BaseChatMemory
from langchain_core.messages import ChatMessage

from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.memory.message import Message
from agentuniverse.base.config.component_configer.configers.memory_configer import MemoryConfiger
from agentuniverse.base.util.logging.logging_util import LOGGER
from agentuniverse.llm.llm import LLM
from law_game_app.app.core.memory.role_langchain_instance import RoleConversationSummaryBufferMemory


class RoleMemory(Memory):
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
    messages: Optional[List[ChatMessage]] = None
    prompt_version: Optional[str] = None

    def as_langchain(self) -> BaseChatMemory:
        """Convert the agentUniverse(aU) chat memory class to the langchain chat memory class."""
        LOGGER.debug('RoleMemory as_langchain')
        if self.llm is None:
            raise ValueError("Must set `llm` when using langchain memory.")
        # if self.type is None or self.type == MemoryTypeEnum.SHORT_TERM:
        #     return AuConversationTokenBufferMemory(llm=self.llm.as_langchain(), memory_key=self.memory_key,
        #                                            input_key=self.input_key, output_key=self.output_key,
        #                                            max_token_limit=self.max_tokens, messages=self.messages)
        # elif self.type == MemoryTypeEnum.LONG_TERM:
        LOGGER.debug(f"RoleMemory as_langchain, self.messages: {self.messages}")
        return RoleConversationSummaryBufferMemory(llm=self.llm.as_langchain(), memory_key=self.memory_key,
                                                   input_key=self.input_key, output_key=self.output_key,
                                                   max_token_limit=self.max_tokens, messages=self.messages,
                                                   prompt_version=self.prompt_version)
