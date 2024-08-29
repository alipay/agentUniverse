# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/29 10:16
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: common_util.py
from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.component.component_configer_util import ComponentConfigerUtil
from agentuniverse.base.component.component_enum import ComponentEnum


def is_component_id_unique(component_id: str, component_type: str) -> bool:
    if component_id is None or component_type is None:
        return True
    component_enum = ComponentEnum.from_value(component_type.upper())
    component_manager_clz = ComponentConfigerUtil.get_component_manager_clz_by_type(component_enum)
    instance: ComponentBase = component_manager_clz().get_instance_obj(component_id)
    return instance is None
