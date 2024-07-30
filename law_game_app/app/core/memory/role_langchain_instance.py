# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time   : 2024/7/29 11:51
# @Author : fluchw
# @Email  : zerozed00@qq.com
# @File   ：role_langchain_instance.py
from typing import List, Optional, Dict, Any

from langchain.memory import ConversationSummaryBufferMemory, ConversationTokenBufferMemory
from langchain.memory.utils import get_prompt_input_key
from langchain_core.messages import BaseMessage, get_buffer_string, ChatMessage
from langchain_core.output_parsers import StrOutputParser

from agentuniverse.agent.memory.enum import ChatMessageEnum
from agentuniverse.base.util.logging.logging_util import LOGGER
from agentuniverse.prompt.prompt import Prompt
from agentuniverse.prompt.prompt_manager import PromptManager


# AuConversationSummaryBufferMemory -> ConversationSummaryBufferMemory -> BaseChatMemory

# 修改于AuConversationSummaryBufferMemory
class RoleConversationSummaryBufferMemory(ConversationSummaryBufferMemory):
    """长期记忆用于存储对话记忆。

    如果记忆超出最大令牌限制，
    记忆将通过 AuConversationSummaryBufferMemory.predict_new_summary 方法进行压缩。

    属性:
        messages (List[BaseMessage]): 保存的 BaseMessage 列表。
    """

    messages: Optional[List[ChatMessage]] = None
    prompt_version: Optional[str] = None

    def __init__(self, **kwargs):
        """初始化方法。

        初始化方法将来自 `messages` 属性的消息保存到记忆缓冲中。

        参数:
            **kwargs: 任意关键字参数。
        """
        LOGGER.debug("kwargs:", kwargs)
        super().__init__(**kwargs)
        self.build_memory()

    @property
    def load_memory(self) -> List[BaseMessage]:
        """通用方法：从记忆缓冲加载记忆上下文。"""
        messages = self.chat_memory.messages
        if self.moving_summary_buffer != "":
            moving_messages: List[BaseMessage] = [
                self.summary_message_cls(content=self.moving_summary_buffer)
            ]
            messages = moving_messages + messages
        return messages

    @property
    def load_memory_str(self) -> str:
        """通用方法：以字符串格式从记忆缓冲加载记忆上下文。"""
        buffer = get_buffer_string(self.chat_memory.messages)
        if self.moving_summary_buffer is not None:
            buffer = self.moving_summary_buffer + buffer
        return buffer

    def build_memory(self):
        """将来自 `messages` 属性的消息的记忆上下文保存到记忆缓冲中。

        注意:
            如果对话消息包含系统消息，则将其保存在 `moving_summary_buffer` 属性中。
        """
        if self.messages is None:
            return
        # 保存系统消息
        for message in self.messages:
            if message.type.lower() == ChatMessageEnum.SYSTEM.value:
                self.moving_summary_buffer += message.content
                self.messages.remove(message)
        # 生成人类和 AI 对话消息对并保存到记忆缓冲

        # 这行不能去掉   必须添加人类的空输入
        # chat_history.append({'role':role,'type': 'chat','content': ''})

        # self.messages.insert(0, ChatMessage(role='role',type='chat', content=''))
        LOGGER.debug(f'self.messages {self.messages}')

        for i in range(0, len(self.messages), 2):
            inputs, outputs = self.generate_chat_messages(ChatMessage(role='role', type='chat', content=''),
                                                          self.messages[i])
            self.save_context(inputs, outputs)
        LOGGER.debug(f'self.messages {self.messages}')

    def generate_chat_messages(self, *pairs: ChatMessage):
        """生成人类和 AI 对话消息对。"""
        return role_generate_chat_messages(self, *pairs)

    def _get_input_output(
            self, inputs: Dict[str, Any], outputs: Dict[str, str]
    ) -> tuple[dict[str, Any], dict[str, str]]:
        if self.input_key is None:
            prompt_input_key = get_prompt_input_key(inputs, self.memory_variables)
        else:
            prompt_input_key = self.input_key
        if self.output_key is None:
            if len(outputs) == 1:
                output_key = list(outputs.keys())[0]
            elif "output" in outputs:
                output_key = "output"
                LOGGER.warn(
                    f"'{self.__class__.__name__}' 得到多个输出键:"
                    f" {outputs.keys()}。默认使用 'output' 键。"
                    f"如果这不是您想要的，请手动设置 'output_key'。"
                )
            else:
                raise ValueError(
                    f"得到多个输出键: {outputs.keys()}，无法 "
                    f"确定要存储在内存中的键。请明确设置 "
                    f"'output_key'。"
                )
        else:
            output_key = self.output_key

        LOGGER.debug(f' inputs {inputs}')
        LOGGER.debug(f' outputs {outputs}')
        return inputs, outputs

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """将对话上下文保存到缓冲区，并修剪记忆。"""

        # super().save_context(inputs, outputs)
        role_save_context(self, inputs, outputs)

    def predict_new_summary(
            self, messages: List[BaseMessage], existing_summary: str
    ) -> str:
        """预测新的摘要，对多轮对话中的记忆进行总结。"""
        new_lines = get_buffer_string(
            messages,
            human_prefix=self.human_prefix,
            ai_prefix=self.ai_prefix,
        )
        prompt_version = self.prompt_version if self.prompt_version else 'chat_memory.summarizer_cn'
        prompt: Prompt = PromptManager().get_instance_obj(prompt_version)
        chain = prompt.as_langchain() | self.llm | StrOutputParser()
        return chain.invoke(input={'summary': existing_summary, 'new_lines': new_lines})

# 修改于AuConversationTokenBufferMemory,但暂未使用
class RoleConversationTokenBufferMemory(ConversationTokenBufferMemory):
    """短期记忆用于存储对话记忆。

    如果记忆超过最大令牌限制，通过截断部分记忆来满足要求。

    属性:
        messages (List[BaseMessage]): 保存的 BaseMessage 列表。
    """

    messages: Optional[List[ChatMessage]] = None

    def __init__(self, **kwargs):
        """初始化方法。

        初始化方法将来自 `messages` 属性的消息保存到记忆缓冲中。

        参数:
            **kwargs: 任意关键字参数。
        """
        super().__init__(**kwargs)
        self.build_memory()

    @property
    def load_memory(self) -> List[BaseMessage]:
        """通用方法：从记忆缓冲加载记忆上下文。"""
        return self.chat_memory.messages

    @property
    def load_memory_str(self) -> str:
        """通用方法：以字符串格式从记忆缓冲加载记忆上下文。"""
        return get_buffer_string(self.chat_memory.messages)

    def build_memory(self):
        """将来自 `messages` 属性的消息的记忆上下文保存到记忆缓冲中。

        注意:
            如果对话消息包含系统消息，则将其从记忆中丢弃。
        """
        if self.messages is None:
            return
        # 丢弃系统消息
        for message in self.messages:
            if message.type.lower() == ChatMessageEnum.SYSTEM.value:
                self.messages.remove(message)
        # 生成人类和 AI 对话消息对并保存到记忆缓冲
        for i in range(0, len(self.messages), 2):
            inputs, outputs = self.generate_chat_messages(self.messages[i], self.messages[i + 1])
            self.save_context(inputs, outputs)

    def generate_chat_messages(self, *pairs: ChatMessage):
        """生成人类和 AI 对话消息对。"""
        return role_generate_chat_messages(self, *pairs)

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """将对话上下文保存到缓冲区并截断部分记忆。"""

        role_save_context(self, inputs, outputs)


def role_save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
    """Save context from the conversation to buffer and prune memories"""

    # super().save_context(inputs, outputs)
    message_list = self.load_memory
    LOGGER.debug(f"message_list {message_list}")
    input_str, output_str = self._get_input_output(inputs, outputs)
    LOGGER.debug(f"input_str {input_str}")
    LOGGER.debug(f"output_str {output_str}")

    self.chat_memory.add_messages(
        [
            # ChatMessage(role=input_str['role'], content=input_str['input']),
            ChatMessage(role=output_str['role'], content=output_str['output'])
        ]
    )

    def message_to_dict(message):
        return {
            "content": message.content,
            "type": message.type,
            'role': message.role
        }

    messages_dicts = []
    for message in message_list:
        messages_dicts.append(message_to_dict(message))
    inputs[self.memory_key] = messages_dicts


def role_generate_chat_messages(self, *pairs: ChatMessage):
    """generate pairs of Human and AI conversation messages"""

    human_dict = {}
    ai_dict = {}

    LOGGER.debug(f"pairs {pairs}")
    for pair in pairs:
        if pair.type.lower() == ChatMessageEnum.HUMAN.value:
            human_dict = {self.input_key: pair.content}
        elif pair.type.lower() == ChatMessageEnum.AI.value:
            ai_dict = {self.output_key: pair.content}
        else:
            human_dict = {'role': pair.role, self.input_key: ''}
            ai_dict = {'role': pair.role, self.output_key: pair.content}

    LOGGER.debug(f"redict {ai_dict}")

    return human_dict, ai_dict
