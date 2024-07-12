#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time   : 2024/7/5 17:16
# @Author : fluchw
# @Email  : zerozed00@qq.com
# @File   ：test.py
from agentuniverse.agent.action.knowledge.knowledge_manager import KnowledgeManager
from agentuniverse.base.agentuniverse import AgentUniverse

AgentUniverse().start()

# /opt/model/agentUniverse/agentuniverse/agent/action/knowledge/knowledge.py
knowledge = KnowledgeManager().get_instance_obj("civil_law_knowledge")
knowledge.query_knowledge(contents="民法")
