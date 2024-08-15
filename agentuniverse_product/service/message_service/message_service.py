# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/1 09:43
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: message_service.py
from datetime import datetime

from agentuniverse_product.dal.message_library import MessageLibrary
from agentuniverse_product.dal.model.message_do import MessageDO


class MessageService:
    """Message Service for aU-product."""

    @staticmethod
    def add_message(session_id: str, content: str, add_time: datetime) -> int:
        """Add a message to the message db table."""
        if content is None:
            raise ValueError("message content is required parameter.")
        return MessageLibrary().add_message(
            MessageDO(session_id=session_id, content=content, gmt_created=add_time, gmt_modified=add_time))
