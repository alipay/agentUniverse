# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/27 11:37
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: memory_util.py
from typing import List

from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.messages import BaseMessage

from agentuniverse.agent.memory.enum import ChatMessageEnum
from agentuniverse.agent.memory.message import Message


def generate_messages(memories: list) -> List[Message]:
    """ Generate a list of messages from the given memories

    Args:
        memories(list): List of memory objects, which can be of type str, dict or Message.

    Returns:
        List[Message]: List of messages
    """
    messages = []
    for m in memories:
        if isinstance(m, Message):
            messages.append(m)
        elif isinstance(m, dict):
            message: Message = Message(type=m.get('type', ''), content=m.get('content', ''))
            messages.append(message)
        elif isinstance(m, str):
            message: Message = Message(type='', content=m)
            messages.append(message)
    return messages


def generate_memories(chat_messages: BaseChatMessageHistory) -> list:
    """Converts the given chat messages into a list of dict messages with content and type.

    Args:
        chat_messages(BaseChatMessageHistory): The langchain chat message history.

    Returns:
        list: the list of messages, with the message type being dict,
        to be given to the user as chat_history in the planner output.
    """
    return [
        {"content": message.content, "type": 'ai' if message.type == 'AIMessageChunk' else message.type}
        for message in chat_messages.messages
    ] if chat_messages.messages else []


def generate_langchain_message(message_list: list[Message]) -> BaseChatMessageHistory:
    """Generate the langchain in-memory chat message history from the given messages.

    Args:
        message_list(list[Message]): The list of messages.

    Returns:
        BaseChatMessageHistory: The langchain chat message history.
    """

    lc_message_history = InMemoryChatMessageHistory()
    if len(message_list) == 0:
        return lc_message_history
    for m in message_list:
        lc_message_history.add_message(BaseMessage(type=m.type, content=m.content))
    return lc_message_history


def generate_message(lc_message: BaseChatMessageHistory, top_k: int = 2) -> list[Message]:
    """Generate the messages from the given langchain chat message history.

    Args:
        lc_message(BaseChatMessageHistory): The langchain chat message history.
        top_k(int): The top k new messages to return.

    Returns:
        list[Message]: The list of messages.
    """
    message_list = []
    if lc_message is None or len(lc_message.messages) == 0:
        return message_list
    top_k_messages = lc_message.messages[-top_k:]
    for m in top_k_messages:
        message_list.append(Message(type=m.type, content=m.content))
    return message_list


def get_memory_string(messages: List[Message]) -> str:
    """Convert the given messages to a string.

    Args:
        messages(List[Message]): The list of messages.

    Returns:
        str: The string representation of the messages.
    """

    string_messages = []
    for m in messages:
        if m.type == ChatMessageEnum.SYSTEM.value:
            role = 'System'
        elif m.type == ChatMessageEnum.HUMAN.value:
            role = 'Human'
        elif m.type == ChatMessageEnum.AI.value:
            role = "AI"
        else:
            role = "default"
        string_messages.append(f"{role}: {m.content}")
    return "\n".join(string_messages)
