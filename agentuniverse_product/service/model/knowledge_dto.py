# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/26 11:02
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: knowledge_dto.py
from typing import Optional

from pydantic import BaseModel, Field


class KnowledgeDTO(BaseModel):
    id: str = Field(description="ID")
    nickname: Optional[str] = Field(description="knowledge nickname", default="")
    description: Optional[str] = Field(description="knowledge description", default="")
