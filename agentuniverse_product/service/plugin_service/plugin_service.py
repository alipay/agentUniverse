# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/27 15:52
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: plugin_service.py
import os
from typing import List

from agentuniverse_product.base.product import Product
from agentuniverse_product.base.product_manager import ProductManager
from agentuniverse_product.base.util.yaml_util import write_yaml_file
from agentuniverse_product.service.model.plugin_dto import PluginDTO
from agentuniverse_product.service.model.tool_dto import ToolDTO
from agentuniverse_product.service.tool_service.tool_service import ToolService
from agentuniverse_product.service.util.agent_util import register_product
from agentuniverse_product.service.util.plugin_util import assemble_plugin_product_config_data, \
    parse_openapi_to_tool_input, parse_openapi_yaml_to_tool_bundle, validate_create_plugin_parameters


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
                                       toolset=product.toolset, openapi_desc=product.openapi_desc)
                res.append(plugin_dto)
        return res

    @staticmethod
    def create_plugin_with_openapi(plugin_dto: PluginDTO) -> str:
        # single OpenAPI schema with multiple APIs is parsed into multiple tool bundles.
        validate_create_plugin_parameters(plugin_dto)
        tool_bundles = parse_openapi_yaml_to_tool_bundle(plugin_dto.openapi_desc)
        for tool in tool_bundles:
            if tool['path'] == '/':
                tool_id = plugin_dto.id
            else:
                tool_id = plugin_dto.id + '_' + tool['path'][1:]
            parameters = parse_openapi_to_tool_input(tool)
            tool_dto = ToolDTO(id=tool_id,
                               nickname=plugin_dto.nickname if plugin_dto.nickname else '',
                               avatar=plugin_dto.avatar if plugin_dto.avatar else '',
                               parameters=parameters,
                               openapi_schema=tool
                               )
            ToolService().create_tool(tool_dto)
        # assemble product config data
        product_config_data = assemble_plugin_product_config_data(plugin_dto)

        # write product YAML file
        product_file_name = f"{plugin_dto.id}_product"
        product_file_path = os.path.join('..', 'core', 'product', 'plugin', f"{product_file_name}.yaml")
        write_yaml_file(product_file_path, product_config_data)
        register_product(product_file_path)
        return plugin_dto.id
