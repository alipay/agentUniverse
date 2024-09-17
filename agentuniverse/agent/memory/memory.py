# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/15 10:05
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: memory.py
from typing import Optional, List

from langchain_core.memory import BaseMemory
from langchain_core.output_parsers import StrOutputParser

from agentuniverse.agent.memory.enum import MemoryTypeEnum
from agentuniverse.agent.memory.message import Message
from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.configers.memory_configer import MemoryConfiger
from agentuniverse.base.util.memory_util import get_memory_string
from agentuniverse.llm.llm import LLM
from agentuniverse.llm.llm_manager import LLMManager
from agentuniverse.prompt.prompt import Prompt
from agentuniverse.prompt.prompt_manager import PromptManager


class Memory(ComponentBase):
    """The basic class for memory model.

    Attributes:
        name (Optional[str]): The name of the memory class.
        description (Optional[str]): The description of the memory class.
        type (MemoryTypeEnum): The type of the memory class including `long-term` and `short-term`.
        memory_key (Optional[str]): The name of the memory key in the prompt.
        max_tokens (int): The maximum number of tokens allowed in the prompt.
        prompt_version (Optional[str]): The version of the prompt to summarize the memory.    llm_name: Optional[str] = None
        llm_name (Optional[str]): The name of the LLM used by this memory.
    """

    name: Optional[str] = ""
    description: Optional[str] = None
    type: MemoryTypeEnum = None
    memory_key: Optional[str] = 'chat_history'
    max_tokens: int = 2000
    prompt_version: Optional[str] = None
    llm_name: Optional[str] = None

    def __init__(self, **kwargs):
        super().__init__(component_type=ComponentEnum.MEMORY, **kwargs)

    def as_langchain(self) -> BaseMemory:
        """Convert the agentUniverse(aU) memory class to the langchain memory class."""
        pass

    def set_by_agent_model(self, **kwargs):
        """ Assign values of parameters to the Memory model in the agent configuration."""
        # note: default shallow copy
        copied_obj = self.model_copy()
        if 'memory_key' in kwargs and kwargs['memory_key']:
            copied_obj.memory_key = kwargs['memory_key']
        if 'max_tokens' in kwargs and kwargs['max_tokens']:
            copied_obj.max_tokens = kwargs['max_tokens']
        if 'prompt_version' in kwargs and kwargs['prompt_version']:
            copied_obj.prompt_version = kwargs['prompt_version']
        if 'llm_name' in kwargs and kwargs['llm_name']:
            copied_obj.llm_name = kwargs['llm_name']
        return copied_obj

    def get_instance_code(self) -> str:
        """Return the full name of the memory."""
        appname = ApplicationConfigManager().app_configer.base_info_appname
        return f'{appname}.{self.component_type.value.lower()}.{self.name}'

    def initialize_by_component_configer(self, component_configer: MemoryConfiger) -> 'Memory':
        """Initialize the memory by the ComponentConfiger object.
        Args:
            component_configer(MemoryConfiger): the ComponentConfiger object
        Returns:
            Memory: the Memory object
        """
        if component_configer.name:
            self.name = component_configer.name
        if component_configer.description:
            self.description = component_configer.description
        if component_configer.type:
            self.type = next((member for member in MemoryTypeEnum if member.value == component_configer.type))
        if component_configer.memory_key:
            self.memory_key = component_configer.memory_key
        if component_configer.max_tokens:
            self.max_tokens = component_configer.max_tokens
        if component_configer.prompt_version:
            self.prompt_version = component_configer.prompt_version
        if component_configer.llm_name:
            self.llm_name = component_configer.llm_name
        return self

    def add(self, message_list: List[Message], **kwargs) -> None:
        """Add messages to the memory."""
        pass

    def delete(self, **kwargs) -> None:
        """Delete messages from the memory."""
        pass

    def get(self, **kwargs) -> List[Message]:
        """Get messages from the memory."""
        pass

    def prune(self, **kwargs) -> None:
        """Prune messages from the memory due to memory max token limitation."""
        pass

    def summarize_memory(
            self, messages: List[Message], max_tokens: int = 500, existing_summary: str = '') -> str:
        """Summarize the memory.

        Args:
            messages (List[Message]): The list of messages to summarize.
            max_tokens (int): The maximum number of tokens allowed in the summary.
            existing_summary (str): The existing summary to append to.

        Returns:
            str: The summary of the memory.
        """
        prompt: Prompt = PromptManager().get_instance_obj(self.prompt_version)
        llm: LLM = LLMManager().get_instance_obj(self.llm_name)
        if prompt and llm:
            memory_str = get_memory_string(messages)
            chain = prompt.as_langchain() | llm.as_langchain() | StrOutputParser()
            return chain.invoke(input={'summary': existing_summary, 'new_lines': memory_str, 'max_tokens': max_tokens})
        else:
            return ''
