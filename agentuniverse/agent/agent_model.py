# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/3/12 15:13
# @Author  : heji
# @Email   : lc299034@antgroup.com
# @FileName: agent_model.py
"""Agent model class."""
from typing import Optional
from pydantic import BaseModel


class AgentModel(BaseModel):
    """The parent class of all agent models, containing only attributes."""

    info: Optional[dict] = dict()
    profile: Optional[dict] = dict()
    plan: Optional[dict] = dict()
    memory: Optional[dict] = dict()
    action: Optional[dict] = dict()
