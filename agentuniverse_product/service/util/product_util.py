# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/27 16:03
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: product_util.py
from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.component.component_configer_util import ComponentConfigerUtil
from agentuniverse.base.component.component_enum import ComponentEnum


def is_id_unique(id: str, type: str) -> bool:
    if id is None or type is None:
        return True
    component_enum = ComponentEnum.from_value(type.upper())
    component_manager_clz = ComponentConfigerUtil.get_component_manager_clz_by_type(component_enum)
    instance: ComponentBase = component_manager_clz().get_instance_obj(id)
    return instance is None
