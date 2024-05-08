# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/3/12 19:22
# @Author  : heji
# @Email   : lc299034@antgroup.com
# @FileName: prompt_model.py
"""Agent Prompt Model module."""
from typing import Optional

from pydantic import BaseModel


class AgentPromptModel(BaseModel):
    """Agent Prompt Model class."""

    introduction: Optional[str] = None
    target: Optional[str] = None
    instruction: Optional[str] = None

    def __add__(self, other):
        """Merge two objects into one object."""
        merged_object = AgentPromptModel()
        for key in set(self.__dict__.keys()).union(other.__dict__.keys()):
            value = getattr(self, key, None)
            if value is None:
                value = getattr(other, key, None)
            setattr(merged_object, key, value)
        return merged_object

    def __bool__(self):
        """ Check whether the object is empty.

        Return True if one of the introduction, target and instruction attribute is not empty.
        Return False otherwise.
        """
        return bool(self.introduction or self.introduction or self.introduction)
