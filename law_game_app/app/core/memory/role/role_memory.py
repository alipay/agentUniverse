# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/11 18:23
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: demo_memory.py
from law_game_app.app.core.memory.role.role_chat_memory import RoleChatMemory


class RoleMemory(RoleChatMemory):
    """The aU demo memory module."""

    def __init__(self, **kwargs):
        """The __init__ method.

        Some parameters, such as name/description/type/memory_key,
        are injected into this class by the demo.yaml configuration.


        Args:
            llm (LLM): the LLM instance used by this memory.
        """
        super().__init__(**kwargs)
