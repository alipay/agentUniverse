# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/25 23:16
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: tool_service.py
from typing import List

from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse_product.base.product import Product
from agentuniverse_product.base.product_manager import ProductManager
from agentuniverse_product.service.model.tool_dto import ToolDTO


class ToolService:
    """Tool Service for aU-product."""

    @staticmethod
    def get_tool_list() -> List[ToolDTO]:
        """Get list of tools."""
        res = []
        product_list: List[Product] = ProductManager().get_instance_obj_list()
        if len(product_list) < 1:
            return res
        for product in product_list:
            if product.type == ComponentEnum.TOOL.value:
                tool_dto = ToolDTO(nickname=product.nickname, avatar=product.avatar, id=product.id)
                tool = product.instance
                tool_dto.description = tool.description
                tool_dto.parameters = tool.input_keys
                res.append(tool_dto)
        return res
