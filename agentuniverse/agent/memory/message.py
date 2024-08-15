# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/28 11:33
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: message.py
from typing import Optional, List, Union, Dict

from langchain_core.messages import HumanMessage
from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, AIMessagePromptTemplate
from langchain_core.prompts.chat import BaseStringMessagePromptTemplate
from pydantic import BaseModel

from agentuniverse.agent.memory.enum import ChatMessageEnum


class Message(BaseModel):
    """The basic class for memory message.

    Attributes:
        type (Optional[str]): The type of the message.
        content (Optional[str]): The content of the message.
    """

    type: Optional[str] = None
    content: Optional[Union[str, List[Union[str, Dict]]]] = None

    def as_langchain(self):
        """Convert the agentUniverse(aU) message class to the langchain message class."""
        if self.type == ChatMessageEnum.SYSTEM.value:
            return SystemMessagePromptTemplate.from_template(self.content)
        elif self.type == ChatMessageEnum.HUMAN.value:
            if isinstance(self.content, str):
                return HumanMessagePromptTemplate.from_template(self.content)
            elif isinstance(self.content, list):
                return HumanMessage(content=self.content)
        elif self.type == ChatMessageEnum.AI.value:
            return AIMessagePromptTemplate.from_template(self.content)
        else:
            return BaseStringMessagePromptTemplate.from_template(self.content)

    @staticmethod
    def as_langchain_list(message_list: List['Message']):
        """Convert agentUniverse(aU) message list to langchain message list """
        langchain_message_list = []
        if message_list is None:
            return langchain_message_list
        for message in message_list:
            langchain_message_list.append(message.as_langchain())
        return langchain_message_list
