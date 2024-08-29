# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/27 23:16
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: plugin_util.py
import re
from typing import Dict
import uuid

from yaml import safe_load
from agentuniverse_product.base.product_manager import ProductManager
from agentuniverse_product.service.model.plugin_dto import PluginDTO


def validate_create_plugin_parameters(plugin_dto: PluginDTO) -> None:
    if plugin_dto.id is None:
        raise ValueError("Plugin id cannot be None.")
    plugin = ProductManager().get_instance_obj(plugin_dto.id)
    if plugin:
        raise ValueError("Plugin instance corresponding to the plugin id already exists.")
    if plugin_dto.openapi_desc is None:
        raise ValueError("The openapi_desc in plugin cannot be None.")


def assemble_plugin_product_config_data(plugin_dto: PluginDTO) -> Dict:
    return {
        'id': plugin_dto.id,
        'nickname': plugin_dto.nickname,
        'avatar': plugin_dto.avatar,
        'type': 'PLUGIN',
        'toolset': plugin_dto.toolset,
        'metadata': {
            'class': 'PluginProduct',
            'module': 'agentuniverse_product.base.plugin_product',
            'type': 'PRODUCT'
        },
        'openapi_desc': plugin_dto.openapi_desc
    }


def parse_openapi_yaml_to_tool_bundle(yaml: str) -> list:
    """
        parse openapi yaml to tool bundle

        :param yaml: the yaml string
        :return: the tool bundle
    """

    openapi: dict = safe_load(yaml)
    if openapi is None:
        raise Exception('Invalid openapi yaml.')

    if len(openapi['servers']) == 0:
        raise Exception('No server found in the openapi yaml.')

    server_url = str(openapi['servers'][0]['url'])

    # list all interfaces
    interfaces = []
    for path, path_item in openapi['paths'].items():
        methods = ['get', 'post', 'put', 'delete',
                   'patch', 'head', 'options', 'trace']
        for method in methods:
            if method in path_item:
                interfaces.append({
                    'path': path,
                    'method': method,
                    'operation': path_item[method],
                    'url': server_url + path,
                })

    for interface in interfaces:
        # create tool bundle
        # check if there is a request body
        if 'requestBody' in interface['operation']:
            request_body = interface['operation']['requestBody']
            if 'content' in request_body:
                for content_type, content in request_body['content'].items():
                    # if there is a reference, get the reference and overwrite the content
                    if 'schema' not in content:
                        continue

                    if '$ref' in content['schema']:
                        # get the reference
                        root = openapi
                        reference = content['schema']['$ref'].split(
                            '/')[1:]
                        for ref in reference:
                            root = root[ref]
                        # overwrite the content
                        interface['operation']['requestBody']['content'][content_type]['schema'] = root

        if 'operationId' not in interface['operation']:
            # remove special characters like / to ensure the operation id is valid ^[a-zA-Z0-9_-]{1,64}$
            path = interface['path']
            if interface['path'].startswith('/'):
                path = interface['path'][1:]
            path = re.sub(r'[^a-zA-Z0-9_-]', '', path)
            if not path:
                path = str(uuid.uuid4())

            interface['operation']['operationId'] = f'{path}_{interface["method"]}'

    return interfaces


def parse_openapi_to_tool_input(openapi: dict) -> list[str]:
    # convert parameters
    parameters = []
    if 'parameters' in openapi['operation']:
        for parameter in openapi['operation'].get('parameters'):
            if parameter.get('required'):
                parameters.append(parameter['name'])
    return parameters
