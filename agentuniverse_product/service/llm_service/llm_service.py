# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/25 23:27
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: llm_service.py
from typing import List

from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse_product.base.constant.llm_constant import LLM_MODEL_NAME
from agentuniverse_product.base.product import Product
from agentuniverse_product.base.product_manager import ProductManager
from agentuniverse_product.service.model.llm_dto import LlmDTO


class LLMService:
    """LLM Service for aU-product."""

    @staticmethod
    def get_llm_list() -> List[LlmDTO]:
        """Get LLM list."""
        res = []
        product_list: List[Product] = ProductManager().get_instance_obj_list()
        if len(product_list) < 1:
            return res
        for product in product_list:
            if product.type == ComponentEnum.LLM.value:
                llm_dto = LlmDTO(nickname=product.nickname, id=product.id)
                llm = product.instance
                llm_dto.temperature = llm.temperature
                llm_dto.model_name = LLM_MODEL_NAME.get(product.id, [])
                res.append(llm_dto)
        return res
