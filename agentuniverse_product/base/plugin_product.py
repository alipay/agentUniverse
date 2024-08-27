# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/27 15:34
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: plugin_product.py
from typing import Optional, List

from agentuniverse.agent.agent import Agent
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse_product.base.product import Product
from agentuniverse_product.base.product_configer import ProductConfiger


class PluginProduct(Product):
    """The basic class of the plugin product."""

    toolset: Optional[List[str]] = list()

    def initialize_by_component_configer(self,
                                         product_configer: ProductConfiger) -> 'PluginProduct':
        """Initialize the Product by the ProductConfiger object.

        Args:
            product_configer(ProductConfiger): A configer contains product basic info.
        Returns:
            PluginProduct: A PluginProduct instance.
        """
        if product_configer.nickname:
            self.nickname = product_configer.nickname
        if product_configer.id:
            self.id = product_configer.id
        if product_configer.type:
            self.type = product_configer.type
        if product_configer.avatar:
            self.avatar = product_configer.avatar
        if hasattr(product_configer, 'toolset') and product_configer.toolset:
            self.toolset = product_configer.toolset
        return self
