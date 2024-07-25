# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/25 19:34
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: session_library.py
import datetime

from sqlalchemy import JSON, Integer, String, DateTime, Column, Index
from sqlalchemy.orm import declarative_base

SESSION_TABLE_NAME = 'session'
Base = declarative_base()


class SessionORM(Base):
    """Sqlalchemy orm Model for session table."""
    __tablename__ = SESSION_TABLE_NAME
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(50), nullable=False)
    agent_id = Column(String(50), nullable=False)
    ext_info = Column(JSON)
    gmt_create = Column(DateTime, default=datetime.datetime.now)
    gmt_modified = Column(DateTime, default=datetime.datetime.now,
                          onupdate=datetime.datetime.now)
    __table_args__ = (
        Index('ix_session_id', 'session_id'),
        Index('ix_agent_id', 'agent_id'),
    )
