# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/5 17:43
# @Author  : weizjajj 
# @Email   : weizhongjie.wzj@antgroup.com
# @FileName: conversation_message.py

import uuid
from typing import Optional, List

from agentuniverse.agent.memory.enum import ChatMessageEnum
from langchain_core.prompts import HumanMessagePromptTemplate, AIMessagePromptTemplate
from langchain_core.prompts.chat import BaseStringMessagePromptTemplate

from agentuniverse.agent.memory.conversation_memory.enum import ConversationMessageSourceType, ConversationMessageEnum
from agentuniverse.agent.memory.message import Message
from agentuniverse.base.context.framework_context_manager import FrameworkContextManager


class ConversationMessage(Message):
    """
    The basic class for conversation memory message

    Attributes:
        id (Optional[str]): Unique identifier.
        trace_id (Optional[str]): Trace ID.
        conversation_id (Optional[str]): Conversation ID.
        source (Optional[str]): Message source.
        source_type (Optional[str]): Type of the message source.
        target (Optional[str]): Message target.
        target_type (Optional[str]): Type of the message target.
        type (Optional[str]): Message type.
        content (Optional[str]): Message content.
        metadata (Optional[dict]): The metadata of the message.
    """
    id: Optional[str | int] = uuid.uuid4().hex
    trace_id: Optional[str] = None
    conversation_id: Optional[str] = None
    source: Optional[str] = None
    source_type: Optional[str] = None
    target: Optional[str] = None
    target_type: Optional[str] = None
    type: Optional[str] = None
    content: Optional[str] = None
    metadata: Optional[dict] = None

    @staticmethod
    def as_langchain_list(message_list: List['ConversationMessage']):
        """Convert agentUniverse(aU) message list to langchain message list """
        messages = []
        for message in message_list:
            # only got agent message
            if message.target_type != ConversationMessageSourceType.AGENT.value:
                continue
            if message.source_type not in [ConversationMessageSourceType.AGENT.value,
                                           ConversationMessageSourceType.USER.value]:
                continue
            if message.source_type == ConversationMessageSourceType.AGENT.value and message.type == ConversationMessageEnum.OUTPUT.value:
                messages.append(message)
            elif message.target_type == ConversationMessageSourceType.AGENT.value and message.type == ConversationMessageEnum.INPUT.value:
                messages.append(message)
        return [message.as_langchain() for message in messages]

    def as_langchain(self):
        """Convert the agentUniverse(aU) message class to the langchain message class."""
        if self.type in [ConversationMessageSourceType.AGENT.value,
                         ConversationMessageSourceType.USER.value]:
            return HumanMessagePromptTemplate.from_template(self.content)
        elif self.type == ChatMessageEnum.AI.value:
            return AIMessagePromptTemplate.from_template(self.content)
        else:
            return BaseStringMessagePromptTemplate.from_template(self.content)

    @classmethod
    def from_dict(cls, data: dict):
        """Convert the agentUniverse(aU) message class to the dict."""
        return cls(**data)

    @classmethod
    def from_message(cls, message: Message, session_id: str):
        message.metadata['prefix'] = '之前对话的摘要：' if message.type == 'summarize' else ''
        message.metadata['params'] = "{}"
        trace_id = message.metadata.get('trace_id')
        if not trace_id:
            trace_id = FrameworkContextManager().get_context('trace_id')
            message.metadata['trace_id'] = trace_id
        return cls(
            id=uuid.uuid4().hex,
            content=message.content,
            metadata=message.metadata,
            type=message.type,
            source=message.source,
            source_type='agent',
            target=message.source,
            target_type='agent',
            trace_id=trace_id,
            conversation_id=message.metadata.get('session_id') if not session_id else session_id,
        )

    @classmethod
    def check_and_convert_message(cls, messages, session_id: str = None):
        if len(messages) == 0:
            return []
        message = messages[0]
        if isinstance(message, cls):
            return messages
        if isinstance(message, Message):
            return [cls.from_message(m, session_id) for m in messages]
