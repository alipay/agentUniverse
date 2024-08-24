# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/6 15:39
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: knowledge_service.py
from typing import List

from agentuniverse.agent.action.knowledge.knowledge import Knowledge
from agentuniverse.agent.action.knowledge.knowledge_manager import KnowledgeManager
from agentuniverse_product.base.product import Product
from agentuniverse_product.base.product_manager import ProductManager
from agentuniverse_product.service.model.knowledge_dto import KnowledgeDTO


class KnowledgeService:
    """Knowledge Service for aU-product."""

    @staticmethod
    def get_knowledge_list() -> List[KnowledgeDTO]:
        """Get all knowledge."""
        res = []
        knowledge_list: List[Knowledge] = KnowledgeManager().get_instance_obj_list()
        if len(knowledge_list) < 1:
            return res
        for knowledge in knowledge_list:
            product: Product = ProductManager().get_instance_obj(knowledge.name)
            knowledge_dto = KnowledgeDTO(nickname=product.nickname if product else '', id=knowledge.name)
            knowledge_dto.description = knowledge.description
            res.append(knowledge_dto)
        return res
