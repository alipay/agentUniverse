# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/14 17:53
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: deploy_base.py
from agentuniverse_data.node.base.model_node_base import ModelNodeBase


class DeployBase(ModelNodeBase):
    """The DeployBase class, which is used to define the base class of deploy node."""

    def _node_preprocess(self) -> None:
        super()._node_preprocess()

    def _node_process(self) -> None:
        pass

    def _node_postprocess(self) -> None:
        super()._node_postprocess()
