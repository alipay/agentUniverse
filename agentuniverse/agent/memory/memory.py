# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/15 10:05
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: memory.py
from typing import Optional

from langchain_core.memory import BaseMemory

from agentuniverse.agent.memory.enum import MemoryTypeEnum
from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.configers.memory_configer import MemoryConfiger


class Memory(ComponentBase):
    """The basic class for memory model.

    Attributes:
        name (Optional[str]): The name of the memory class.
        description (Optional[str]): The description of the memory class.
        type (MemoryTypeEnum): The type of the memory class including `long-term` and `short-term`.
        memory_key (Optional[str]): The name of the memory key in the prompt.
        max_tokens (int): The maximum number of tokens allowed in the memory.
    """

    name: Optional[str] = ""
    description: Optional[str] = None
    type: MemoryTypeEnum = None
    memory_key: Optional[str] = 'chat_history'
    max_tokens: int = 2000

    def __init__(self, **kwargs):
        super().__init__(component_type=ComponentEnum.MEMORY, **kwargs)

    def as_langchain(self) -> BaseMemory:
        """Convert the AgentUniverse(AU) memory class to the langchain memory class."""
        pass

    def set_by_agent_model(self, **kwargs) -> None:
        """ Assign values of parameters to the Memory model in the agent configuration."""
        if 'memory_key' in kwargs and kwargs['memory_key']:
            self.memory_key = kwargs['memory_key']
        if 'max_tokens' in kwargs and kwargs['max_tokens']:
            self.max_tokens = kwargs['max_tokens']

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
        return self
