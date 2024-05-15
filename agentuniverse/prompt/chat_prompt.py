# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/5/14 14:41
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: chat_prompt.py
from typing import List
import re

from langchain_core.prompts import ChatPromptTemplate

from agentuniverse.agent.memory.message import Message
from agentuniverse.base.util.prompt_util import generate_chat_template
from agentuniverse.prompt.prompt import Prompt
from agentuniverse.prompt.prompt_model import AgentPromptModel


class ChatPrompt(Prompt):
    messages: List[Message] = []

    def as_langchain(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages(Message.as_langchain_list(self.messages))

    def build_prompt(self, agent_prompt_model: AgentPromptModel, prompt_assemble_order: list[str]) -> 'ChatPrompt':
        """Build the prompt class.

        Args:
            agent_prompt_model (AgentPromptModel): The user agent prompt model.
            prompt_assemble_order (list[str]): The prompt assemble ordered list.

        Returns:
            ChatPrompt: The chat prompt object.
        """
        self.messages = generate_chat_template(agent_prompt_model, prompt_assemble_order)
        self.input_variables = self.extract_placeholders()
        return self

    def extract_placeholders(self) -> List[str]:
        """Extract the placeholders from the messages.

        Returns:
            List[str]: The placeholders list.
        """
        result = []
        placeholder_pattern = re.compile(r'\{(.*?)}')
        for message in self.messages:
            matches = placeholder_pattern.findall(message.content)
            result.extend(matches)
        return result
