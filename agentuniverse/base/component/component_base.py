# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/14 15:35
# @Author  : jerry.zzw 
# @Email   : jerry.zzw@antgroup.com
# @FileName: component_base.py
from abc import ABC

from pydantic import BaseModel, ConfigDict

from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger


class ComponentBase(BaseModel):
    """组件基类，用于定义组件的基础类."""

    component_type: ComponentEnum
    # Pydantic 的受保护命名空间配置
    model_config = ConfigDict(protected_namespaces=())

    def get_instance_code(self) -> str:
        """返回组件的完整名称."""
        appname = ApplicationConfigManager().app_configer.base_info_appname
        return f'{appname}.{self.component_type.value.lower()}.{self.name}'

    def initialize_by_component_configer(self, component_configer: ComponentConfiger) -> 'ComponentBase':
        """通过 ComponentConfiger 对象初始化组件.

        参数:
            component_configer (ComponentConfiger): ComponentConfiger 对象
        返回:
            ComponentBase: 组件对象
        """
        pass
