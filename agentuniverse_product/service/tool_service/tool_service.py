# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/25 23:16
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: tool_service.py
from typing import List

from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse_product.base.product import Product
from agentuniverse_product.base.product_manager import ProductManager
from agentuniverse_product.service.model.tool_dto import ToolDTO


class ToolService:
    """Tool Service for aU-product."""

    @staticmethod
    def get_tool_list() -> List[ToolDTO]:
        """Get list of tools."""
        res = []
        tool_list: List[Tool] = ToolManager().get_instance_obj_list()
        if len(tool_list) < 1:
            return res
        for tool in tool_list:
            product: Product = ProductManager().get_instance_obj(tool.name)
            tool_dto = ToolDTO(nickname=product.nickname if product else '', avatar=product.avatar if product else '',
                               id=tool.name)
            tool_dto.description = tool.description
            tool_dto.parameters = tool.input_keys
            res.append(tool_dto)
        return res
