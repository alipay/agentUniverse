# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/26 18:23
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: default_memory.py
from agentuniverse.agent.memory.chat_memory import ChatMemory
from agentuniverse.llm.openai_llm import OpenAILLM


class DefaultMemory(ChatMemory):
    """The AFAF default memory module."""

    def __init__(self, **kwargs):
        """The __init__ method.

        Some parameters, such as name/description/type/memory_key,
        are injected into this class by the default_memory.yaml configuration.


        Args:
            llm (LLM): the LLM instance used by this memory.
            default memory uses OpenAILLM(gpt-3.5-turbo) object as the memory llm.
        """
        super().__init__(**kwargs)
        self.llm = OpenAILLM(model_name="gpt-3.5-turbo")
