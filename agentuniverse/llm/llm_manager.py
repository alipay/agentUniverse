# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/4/2 16:18
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: llm_manager.py
from agentuniverse.base.annotation.singleton import singleton
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.component.component_manager_base import ComponentManagerBase


@singleton
class LLMManager(ComponentManagerBase):
    """The LLMManager class, which is used to manage the LLMs."""

    def __init__(self):
        """Initialize the LLMManager."""
        super().__init__(ComponentEnum.LLM)
