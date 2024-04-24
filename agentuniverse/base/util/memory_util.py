# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/27 11:37
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: memory_util.py
from typing import List

from agentuniverse.agent.memory.message import Message


def generate_messages(memories: list) -> List[Message]:
    messages = []
    for memory in memories:
        message: Message = Message(type=memory.get('type'), content=memory.get('content'))
        messages.append(message)
    return messages
