# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/27 11:37
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: memory_util.py
from typing import List

from langchain_core.chat_history import BaseChatMessageHistory

from agentuniverse.agent.memory.message import Message


def generate_messages(memories: list) -> List[Message]:
    messages = []
    for memory in memories:
        message: Message = Message(type=memory.get('type'), content=memory.get('content'))
        messages.append(message)
    return messages


def generate_memories(chat_messages: BaseChatMessageHistory) -> list:
    return [
        {"content": message.content, "type": 'ai' if message.type == 'AIMessageChunk' else message.type}
        for message in chat_messages.messages
    ] if chat_messages.messages else []
