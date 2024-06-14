# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/14 17:05
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: dataflow.py
import importlib
import sys
import traceback
from typing import List, Optional

from pydantic import BaseModel

from agentuniverse.base.util.logging.logging_util import LOGGER
from agentuniverse.base.config.configer import Configer
from agentuniverse_data.node.base.node_base import NodeBase


class Dataflow(BaseModel):
    """The Dataflow class, which is used to define the class of data flow."""

    _flow_name: str = None
    _flow_desc: str = None
    _node_sequence_list: List[NodeBase] = None

    _configer: Optional[Configer] = None

    def __init__(self, conf_path: str = None):
        super().__init__()
        if conf_path:
            self._configer = Configer(conf_path)

    def _flow_preprocess(self) -> None:
        self._configer.load()
        self._flow_name = self._configer.get('name')
        self._flow_desc = self._configer.get('description')

        nodes = self._configer.get('nodes')
        if not nodes:
            LOGGER.error('no nodes in yaml conf')
            return

        self._node_sequence_list = []
        for i in range(0, len(nodes)):
            node_obj = nodes[i]
            module_str = node_obj.get('module')
            class_str = node_obj.get('class')
            param_in_jsonl_str = node_obj.get('param_in_jsonl')
            param_out_json_str = node_obj.get('param_out_jsonl')
            datasets_in_jsonl_list = node_obj.get('datasets_in_jsonl')
            dataset_out_jsonl_str = node_obj.get('dataset_out_jsonl')
            node_param_json = node_obj.get('node_param')

            module = importlib.import_module(module_str)
            clz = getattr(module, class_str)
            node: NodeBase = clz()
            node.set_param_in_jsonl(param_in_jsonl_str)
            node.set_param_out_jsonl(param_out_json_str)
            node.set_datasets_in_jsonl(datasets_in_jsonl_list)
            node.set_dataset_out_jsonl(dataset_out_jsonl_str)
            node.set_node_param_json(node_param_json)

            self._node_sequence_list.append(node)

        return

    def _flow_process(self) -> None:
        if self._node_sequence_list:
            for i in range(0, len(self._node_sequence_list)):
                self._node_sequence_list[i].execute()

    def _flow_postprocess(self) -> None:
        pass

    def execute(self) -> None:
        try:
            self._flow_preprocess()
            self._flow_process()
            self._flow_postprocess()
        except Exception as e:
            # logging later
            LOGGER.warn(e)
            LOGGER.warn(traceback.format_exc())
            LOGGER.warn(traceback.extract_tb(sys.exc_info()))
