# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/25 23:16
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: tool_service.py
import os
from typing import List

from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse_product.base.product import Product
from agentuniverse_product.base.product_manager import ProductManager
from agentuniverse_product.base.util.yaml_util import write_yaml_file
from agentuniverse_product.service.model.tool_dto import ToolDTO
from agentuniverse_product.service.util.agent_util import register_product
from agentuniverse_product.service.util.tool_util import assemble_api_tool_config_data, \
    assemble_tool_product_config_data, register_tool, validate_create_api_tool_parameters


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

    @staticmethod
    def create_tool(tool_dto: ToolDTO) -> str:
        # validate parameters
        validate_create_api_tool_parameters(tool_dto)

        # assemble product config data
        product_config_data = assemble_tool_product_config_data(tool_dto)

        # write product YAML file
        product_file_name = f"{tool_dto.id}_product"
        product_file_path = os.path.join('..', 'core', 'product', 'tool', f"{product_file_name}.yaml")
        write_yaml_file(product_file_path, product_config_data)

        # assemble tool config data
        tool_config_data = assemble_api_tool_config_data(tool_dto)

        # write tool YAML file
        tool_file_path = os.path.join('..', 'core', 'tool', f"{tool_dto.id}.yaml")
        write_yaml_file(tool_file_path, tool_config_data)

        # register product and tool instance
        register_tool(tool_file_path)
        register_product(product_file_path)
        return tool_dto.id
