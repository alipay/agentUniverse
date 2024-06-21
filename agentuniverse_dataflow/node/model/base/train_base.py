# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/14 17:54
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: train_base.py
from agentuniverse_dataflow.node.base.model_node_base import ModelNodeBase


class TrainBase(ModelNodeBase):
    """The TrainBase class, which is used to define the base class of train node."""

    train_out_artifact: str = None

    def _node_preprocess(self) -> None:
        super()._node_preprocess()

    def _node_process(self) -> None:
        pass

    def _node_postprocess(self) -> None:
        super()._node_postprocess()
