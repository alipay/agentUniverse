# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/21 11:34
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: workflow_config.py
from typing import Optional, List

from pydantic import BaseModel, ConfigDict


class ParameterConfig(BaseModel):
    name: Optional[str] = None
    selector: Optional[List[str]] = None
    value: Optional[str] = None


class LLMConfig(BaseModel):
    id: str
    temperature: float
    model_name: str
    # pydantic protected_namespaces config
    model_config = ConfigDict(protected_namespaces=())


class RetrivalConfig(BaseModel):
    top_k: int
