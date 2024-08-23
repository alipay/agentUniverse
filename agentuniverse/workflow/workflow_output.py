# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/21 14:24
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: workflow_output.py
from typing import Optional, Dict, Any

from pydantic import BaseModel

from agentuniverse.workflow.node.node_output import NodeOutput


class WorkflowOutput(BaseModel):
    """The basic class of the workflow output."""

    workflow_id: str = None
    metadata: Optional[Dict[str, Any]] = None
    workflow_parameters: Optional[Dict[int, Dict]] = dict()
    workflow_node_results: Optional[Dict[int, NodeOutput]] = dict()
