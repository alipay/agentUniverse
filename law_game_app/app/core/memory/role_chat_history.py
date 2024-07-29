#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time   : 2024/7/22 11:15
# @Author : fluchw
# @Email  : zerozed00@qq.com
# @File   ：role_chat_history.py
"""**Chat message history** stores a history of the message interactions in a chat.


**Class hierarchy:**

.. code-block::

    BaseChatMessageHistory --> <name>ChatMessageHistory  # Examples: FileChatMessageHistory, PostgresChatMessageHistory

**Main helpers:**

.. code-block::

    AIMessage, HumanMessage, BaseMessage

"""  # noqa: E501
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Sequence, Union

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    get_buffer_string,
)
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.runnables import run_in_executor


class RoleChatMessageHistory(BaseChatMessageHistory):

    messages: List[BaseMessage]
    """A property or attribute that returns a list of messages.

    In general, getting the messages may involve IO to the underlying
    persistence layer, so this operation is expected to incur some
    latency.
    """

    def add_message(self, message: BaseMessage) -> None:
        """Add a Message object to the store.

        Args:
            message: A BaseMessage object to store.
        """
        if type(self).add_messages != BaseChatMessageHistory.add_messages:
            # This means that the sub-class has implemented an efficient add_messages
            # method, so we should use it.
            self.add_messages([message])
        else:
            raise NotImplementedError(
                "add_message is not implemented for this class. "
                "Please implement add_message or add_messages."
            )

    def add_messages(self, messages: Sequence[BaseMessage]) -> None:
        """Add a list of messages.

        Implementations should over-ride this method to handle bulk addition of messages
        in an efficient manner to avoid unnecessary round-trips to the underlying store.

        Args:
            messages: A list of BaseMessage objects to store.
        """
        for message in messages:
            self.add_message(message)


    @abstractmethod
    def clear(self) -> None:
        """Remove all messages from the store"""

    async def aclear(self) -> None:
        """Remove all messages from the store"""
        await run_in_executor(None, self.clear)

    def __str__(self) -> str:
        """Return a string representation of the chat history."""
        return get_buffer_string(self.messages)


class InMemoryChatMessageHistory(BaseChatMessageHistory, BaseModel):
    """In memory implementation of chat message history.

    Stores messages in an in memory list.
    """

    messages: List[BaseMessage] = Field(default_factory=list)

    async def aget_messages(self) -> List[BaseMessage]:
        return self.messages

    def add_message(self, message: BaseMessage) -> None:
        """Add a self-created message to the store"""
        self.messages.append(message)

    async def aadd_messages(self, messages: Sequence[BaseMessage]) -> None:
        """Add messages to the store"""
        self.add_messages(messages)

    def clear(self) -> None:
        self.messages = []

    async def aclear(self) -> None:
        self.clear()
