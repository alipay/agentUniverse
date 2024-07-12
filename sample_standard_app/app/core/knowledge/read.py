#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time   : 2024/7/5 17:08
# @Author : fluchw
# @Email  : zerozed00@qq.com
# @File   ：read.py
from agentuniverse.agent.action.knowledge.knowledge_manager import KnowledgeManager
# /opt/model/agentUniverse/agentuniverse/agent/action/knowledge/knowledge.py
knowledge = KnowledgeManager().get_instance_obj("cicil_law_knowledge")
knowledge.query_knowledge("刑法")