# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/28 11:33
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: message.py
from typing import Optional

from pydantic import BaseModel


class Message(BaseModel):
    """The basic class for memory message.

    Attributes:
        type (Optional[str]): The type of the message.
        content (Optional[str]): The content of the message.
    """

    type: Optional[str] = None
    content: Optional[str] = None
