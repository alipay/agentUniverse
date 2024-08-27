from typing import Dict
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
        'metadata': {
            'class': 'Product',
            'module': 'agentuniverse_product.base.product',
            'type': 'PRODUCT'
        },
        'toolset': ['google_search_tool']
    }

