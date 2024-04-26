# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/26 17:57
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: memory_manager.py
from agentuniverse.base.annotation.singleton import singleton
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.component.component_manager_base import ComponentManagerBase


@singleton
class MemoryManager(ComponentManagerBase):
    """The MemoryManager class, which is used to manage memories."""

    def __init__(self):
        """Initialize the MemoryManager."""
        super().__init__(ComponentEnum.MEMORY)
