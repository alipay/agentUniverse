# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/27 11:37
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: memory_util.py
from typing import List

from langchain_core.chat_history import BaseChatMessageHistory

from agentuniverse.agent.memory.enum import ChatMessageEnum
from agentuniverse.agent.memory.message import Message
from agentuniverse.llm.llm import LLM
from agentuniverse.llm.llm_manager import LLMManager


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
            messages.append(Message.from_dict(m))
        elif isinstance(m, str):
            message: Message = Message(content=m, metadata={})
            messages.append(message)
    return messages


def generate_memories(chat_messages: BaseChatMessageHistory) -> list:
    return [
        {"content": message.content, "type": 'ai' if message.type == 'AIMessageChunk' else message.type}
        for message in chat_messages.messages
    ] if chat_messages.messages else []


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
            role = ""
        m_str = ""
        if role:
            m_str += f"Message role: {role} "
        if m.source:
            m_str += f"Message source: {m.source} "
        m_str += f"Message content: \n {m.content} "
        string_messages.append(m_str)
    return "\n\n".join(string_messages)


def get_memory_tokens(memories: List[Message], llm_name: str = None) -> int:
    """Get the number of tokens in the given memories.

    Args:
        memories(List[Message]): The list of messages.
        llm_name(str): The name of the LLM to use for token counting.

    Returns:
        int: The number of tokens in the given memories.
    """
    memory_str = get_memory_string(memories)
    llm_instance: LLM = LLMManager().get_instance_obj(llm_name)
    return llm_instance.get_num_tokens(memory_str) if llm_instance else len(memory_str)
