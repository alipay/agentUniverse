# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/6 15:39
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: knowledge_service.py
from typing import List

from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse_product.base.product import Product
from agentuniverse_product.base.product_manager import ProductManager
from agentuniverse_product.service.model.knowledge_dto import KnowledgeDTO


class KnowledgeService:
    """Knowledge Service for aU-product."""

    @staticmethod
    def get_knowledge_list() -> List[KnowledgeDTO]:
        """Get all knowledge."""
        res = []
        product_list: List[Product] = ProductManager().get_instance_obj_list()
        if len(product_list) < 1:
            return res
        for product in product_list:
            if product.type == ComponentEnum.KNOWLEDGE.value:
                knowledge_dto = KnowledgeDTO(nickname=product.nickname, id=product.id)
                knowledge = product.instance
                knowledge_dto.description = knowledge.description
                res.append(knowledge_dto)
        return res
