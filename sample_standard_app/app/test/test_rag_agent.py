# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/4/1 14:32
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: test_rag_agent.py
import unittest

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.base.agentuniverse import AgentUniverse


class RagAgentTest(unittest.TestCase):
    """
    Test cases for the rag agent
    """

    def setUp(self) -> None:
        AgentUniverse().start(config_path='../../config/config.toml')

    def test_rag_agent(self):
        """Test demo rag agent."""
        instance: Agent = AgentManager().get_instance_obj('demo_rag_agent')
        output_object: OutputObject = instance.run(input='英伟达股票大涨原因是什么？')
        print(output_object.get_data('output'))


if __name__ == '__main__':
    unittest.main()
