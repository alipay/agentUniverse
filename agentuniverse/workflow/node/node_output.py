# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/20 20:03
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: node_output.py
from typing import Optional, Dict, Any

from pydantic import BaseModel

from agentuniverse.workflow.node.enum import NodeStatusEnum


class NodeOutput(BaseModel):
    """The basic class of the node output."""

    node_id: Optional[str] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    status: NodeStatusEnum = NodeStatusEnum.RUNNING
    metadata: Optional[Dict[str, Any]] = None
    edge_source_handler: Optional[str] = None
