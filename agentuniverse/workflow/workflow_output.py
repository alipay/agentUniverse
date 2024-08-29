# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/21 14:24
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: workflow_output.py
from typing import Optional, Dict, Any, List

from pydantic import BaseModel

from agentuniverse.workflow.node.node_config import NodeOutputParams
from agentuniverse.workflow.node.node_output import NodeOutput


class WorkflowOutput(BaseModel):
    """The basic class of the workflow output."""

    workflow_id: str = None
    metadata: Optional[Dict[str, Any]] = dict()
    workflow_parameters: Optional[Dict[str, List[NodeOutputParams]]] = dict()
    workflow_node_results: Optional[Dict[str, NodeOutput]] = dict()
    workflow_start_params: Optional[Dict[str, Any]] = dict()
    workflow_end_params: Optional[Dict[str, Any]] = dict()
