# -*- coding:utf-8 -*-

# @Time    : 2024/4/23 14:58
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: test_rag_agent.py
import unittest

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.base.agentuniverse import AgentUniverse


class TestAgent(unittest.TestCase):

    def setUp(self) -> None:
        AgentUniverse().start(config_path='./config.toml')

    def test_rag_agent(self):
        instance: Agent = AgentManager().get_instance_obj('rag_agent')
        output_object: OutputObject = instance.run(input='分析下先锋领航退出中国的原因')
        print(output_object.get_data('output'))
