# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/25 21:52
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: agent_dto.py
from typing import Optional

from pydantic import BaseModel, Field


class AgentDTO(BaseModel):
    id: str = Field(description="ID")
    nickname: Optional[str] = Field(description="agent nickname", default="")
    avatar: Optional[str] = Field(description="agent avatar path", default="")
    description: Optional[str] = Field(description="agent description", default="")
