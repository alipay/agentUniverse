#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time   : 2024/7/18 16:16
# @Author : fluchw
# @Email  : zerozed00@qq.com
# @File   ：role_message.py
from typing import Optional, List, Union, Dict

from langchain_core.messages import HumanMessage
from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, AIMessagePromptTemplate
from langchain_core.prompts.chat import BaseStringMessagePromptTemplate
from pydantic import BaseModel

from agentuniverse.agent.memory.enum import ChatMessageEnum
from agentuniverse.agent.memory.message import Message
from agentuniverse.base.util.logging.logging_util import LOGGER


class RoleMessage(Message):
    """The basic class for memory message.

    Attributes:
        type (Optional[str]): The type of the message.
        content (Optional[str]): The content of the message.
    """
    role: str = None
    type: Optional[str] = None
    content: Union[str, List[Union[str, Dict]]] = None

    def as_langchain(self):
        """Convert the agentUniverse(aU) message class to the langchain message class."""
        LOGGER.debug(f"触发 as_langchain")

        if self.type == ChatMessageEnum.SYSTEM.value:

            return SystemMessagePromptTemplate.from_template(self.content)

        elif self.type == ChatMessageEnum.HUMAN.value:
            LOGGER.debug(f"触发 ChatMessageEnum.HUMAN")

            if isinstance(self.content, str):
                return HumanMessagePromptTemplate.from_template(self.content)

            elif isinstance(self.content, list):
                return HumanMessage(content=self.content)

        elif self.type == ChatMessageEnum.AI.value:
            return AIMessagePromptTemplate.from_template(self.content)

        else:
            return BaseStringMessagePromptTemplate.from_template(self.content)
