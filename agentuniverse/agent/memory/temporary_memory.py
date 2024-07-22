# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/17 15:23
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: temporary_memory.py
from typing import Optional, List, Dict

from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.memory.message import Message
from agentuniverse.base.util.memory_util import get_memory_string
from agentuniverse.llm.llm_manager import LLMManager


class TemporaryMemory(Memory):
    """TemporaryMemory class that stores temporary messages in a list.

    Short-term memory: it is used to store messages that are not saved in the long-term memory.

    Attributes:
        messages (Dict[str, List[Message]]): A dictionary that stores the messages of each session.
        llm_name (Optional[str]): The name of the LLM used to calculate the memory tokens.
    """

    messages: Dict[str, List[Message]] = {}
    llm_name: Optional[str] = None

    def clear(self, session_id='', **kwargs) -> None:
        """Clear the memory from the `messages`."""
        session_messages = self.messages.get(session_id, [])
        session_messages.clear()

    def add(self, message_list: List[Message], session_id: str = '', **kwargs) -> None:
        """Add messages to the `messages`."""
        if message_list is None:
            return
        session_messages = self.messages.get(session_id, [])
        session_messages.extend(message_list)
        self.messages[session_id] = session_messages

    def delete(self, index_list: List[int], session_id: str = '', **kwargs) -> None:
        """Delete messages from the `messages` by index."""
        if index_list is None:
            return
        session_messages = self.messages.get(session_id, [])
        if len(session_messages) > 0:
            for index in index_list:
                if 0 <= index < len(session_messages):
                    session_messages.pop(index)

    def get(self, session_id: str = '', **kwargs) -> List[Message]:
        """Get messages from the `messages` by session id."""
        session_messages = self.messages.get(session_id, [])
        return self.prune(session_messages, session_id)

    def prune(self, message_list: List[Message], session_id: str = '', **kwargs) -> List[Message]:
        """Prune messages from the memory due to memory max token limitation."""
        if len(message_list) < 1:
            return []
        # truncate the memory if it exceeds the maximum number of tokens
        prune_messages = message_list[:]
        if self.llm_name:
            session_message_str = get_memory_string(message_list)
            llm_instance = LLMManager().get_instance_obj(self.llm_name)
            message_tokens = llm_instance.get_num_tokens(session_message_str)

            if message_tokens > self.max_tokens:
                while message_tokens > self.max_tokens:
                    prune_messages.pop(0)
                    message_tokens = llm_instance.get_num_tokens(get_memory_string(prune_messages))
        return prune_messages

    def set_by_agent_model(self, **kwargs):
        """ Assign values of parameters to the Memory model in the agent configuration."""
        # note: default shallow copy
        copied_obj = super().set_by_agent_model(**kwargs)
        if 'llm_name' in kwargs and kwargs['llm_name']:
            copied_obj.llm_name = kwargs['llm_name']
        return copied_obj
