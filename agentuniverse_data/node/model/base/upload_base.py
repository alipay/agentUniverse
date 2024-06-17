# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/14 17:59
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: upload_base.py
from agentuniverse_data.node.base.model_node_base import ModelNodeBase


class UploadBase(ModelNodeBase):
    """The UploadBase class, which is used to define the base class of upload node."""

    dataset_jsonl_filename: str = None

    def __init__(self, **kwargs):
        super().__init__()
        self.set_flow_start_node()

    def _node_preprocess(self) -> None:
        super()._node_preprocess()
        if self.datasets_in_jsonl and len(self.datasets_in_jsonl) > 0:
            self.dataset_jsonl_filename = self.datasets_in_jsonl[0] + '.jsonl'

    def _node_process(self) -> None:
        pass

    def _node_postprocess(self) -> None:
        super()._node_postprocess()
