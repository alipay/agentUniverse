# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/14 15:35
# @Author  : jerry.zzw 
# @Email   : jerry.zzw@antgroup.com
# @FileName: component_base.py
from abc import ABC

from pydantic import BaseModel

from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger


class ComponentBase(BaseModel):
    """The ComponentBase class, which is used to define the base class of the component."""

    component_type: ComponentEnum

    def get_instance_code(self) -> str:
        """Return the full name of the component."""
        appname = ApplicationConfigManager().app_configer.base_info_appname
        return f'{appname}.{self.component_type.value.lower()}.{self.name}'

    def initialize_by_component_configer(self, component_configer: ComponentConfiger) -> 'ComponentBase':
        """Initialize the component by the ComponentConfiger object.

        Args:
            component_configer(ComponentConfiger): the ComponentConfiger object
        Returns:
            ComponentBase: the component object
        """
        pass
