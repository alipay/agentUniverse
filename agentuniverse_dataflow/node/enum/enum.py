# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/14 17:07
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: enum.py
from enum import Enum


class NodeEnum(Enum):
    """The enumeration of the supported nodes."""

    # DATA
    PROMPT = "PROMPT"
    PROMPT_ANSWER = "PROMPT_ANSWER"

    # MODEL
    MODEL = "MODEL"

    # CRITIC
    EVAL = "EVAL"
    QUALITY = "QUALITY"

    @staticmethod
    def to_value_list():
        """Return the value list of the enumeration."""
        return [item.value for item in NodeEnum]


class InOutEnum(Enum):
    """The enumeration of the supported inputs and outputs."""

    JSONL = "JSONL"

    @staticmethod
    def to_value_list():
        """Return the value list of the enumeration."""
        return [item.value for item in InOutEnum]
