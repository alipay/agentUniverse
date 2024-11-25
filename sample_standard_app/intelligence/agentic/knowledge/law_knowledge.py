# !/usr/bin/env python3
# -*- coding:utf-8 -*-
from typing import List, Any

# @Time    : 2024/8/14 15:54
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: law_knowledge.py
import json

from agentuniverse.agent.action.knowledge.knowledge import Knowledge
from agentuniverse.agent.action.knowledge.store.document import Document


class LawKnowledge(Knowledge):
    def to_llm(self, retrieved_docs: List[Document]) -> Any:
        return """
《民法典》第1019条：
肖像权的内容：肖像权人享有对其肖像的专有权利，未经本人同意，不得制作、使用、公开其肖像。
例外情形：如果属于合理使用情形（如为公共利益或者个人在公共场所的非恶意拍摄），不构成侵权。
==========================
民法典》第1032条：
删除请求：如果李四认为照片的存在或传播对其个人权益造成实际侵害，可以要求删除。
张三的抗辩：如果拍摄行为合理且照片未被恶意使用或传播，李四的删除要求可能缺乏法律依据。
"""
