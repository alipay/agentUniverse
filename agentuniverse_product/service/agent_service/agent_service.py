# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/25 21:11
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: agent_service.py
from typing import List

from agentuniverse.agent.agent_model import AgentModel
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse_product.base.product.product import Product
from agentuniverse_product.base.product.product_manager import ProductManager
from agentuniverse_product.service.agent_service.model.agent_dto import AgentDTO


class AgentService:

    @staticmethod
    def get_agent_list() -> List[AgentDTO]:
        res = []
        product_list: List[Product] = ProductManager().get_instance_obj_list()
        if len(product_list) < 1:
            return res
        for product in product_list:
            if product.type == ComponentEnum.AGENT.value:
                agent_dto = AgentDTO(nickname=product.nickname, avatar=product.avatar, id=product.id)
                agent = product.instance
                agent_model: AgentModel = agent.agent_model
                agent_dto.description = agent_model.info.get('description', '')
                res.append(agent_dto)
        return res
