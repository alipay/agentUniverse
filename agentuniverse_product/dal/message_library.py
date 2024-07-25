# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/25 19:34
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: message_library.py
import datetime

from sqlalchemy import JSON, Integer, String, DateTime, Column, Index
from sqlalchemy.orm import declarative_base

MESSAGE_TABLE_NAME = 'message'
Base = declarative_base()


class MessageORM(Base):
    """Sqlalchemy orm Model for message table."""
    __tablename__ = MESSAGE_TABLE_NAME
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(50), nullable=False)
    message = Column(JSON)
    ext_info = Column(JSON)
    gmt_create = Column(DateTime, default=datetime.datetime.now)
    gmt_modified = Column(DateTime, default=datetime.datetime.now,
                          onupdate=datetime.datetime.now)
    __table_args__ = (
        Index('ix_session_id', 'session_id'),
    )
