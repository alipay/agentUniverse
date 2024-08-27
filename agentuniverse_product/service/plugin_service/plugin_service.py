# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/27 15:52
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: plugin_service.py
from typing import List

from agentuniverse_product.base.product import Product
from agentuniverse_product.base.product_manager import ProductManager
from agentuniverse_product.service.model.plugin_dto import PluginDTO


class PluginService:
    """Plugin Service for aU-product."""

    @staticmethod
    def get_plugin_list() -> List[PluginDTO]:
        """Get list of plugins."""
        res = []
        product_list: List[Product] = ProductManager().get_instance_obj_list()
        if len(product_list) < 1:
            return res
        for product in product_list:
            if product.type == 'PLUGIN':
                plugin_dto = PluginDTO(nickname=product.nickname, avatar=product.avatar, id=product.id,
                                       description=product.description, toolset=product.toolset)
                res.append(plugin_dto)
        return res
