# !/usr/bin/env python3
# -*- coding:utf-8 -*-
import time
# @Time    : 2024/4/1 14:32
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: test_rag_agent.py
import unittest

from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.memory.memory_manager import MemoryManager

from agentuniverse.base.agentuniverse import AgentUniverse


class RagAgentTest(unittest.TestCase):
    """
    Test cases for the rag agent
    """

    def setUp(self) -> None:
        AgentUniverse().start(config_path='../../config/config.toml')
    #
    def test_query_conversation_memory(self):
        trace_id = "0faed903-4d8e-47f5-a773-ab829f88455d"
        session_id="session001"
        memory_instance:Memory = MemoryManager().get_instance_obj("demo_memory_d")
        #
        # messages = memory_instance.get_with_no_prune(session_id="test_weizj_001")
        # print(messages)

        res = memory_instance.get(session_id=session_id)

        print(res)

    # def test_rag_agent(self):
    #     """Test demo rag agent."""
    #     FrameworkContextManager().set_context("session_id","test_weizj_001")
    #     FrameworkContextManager().get_context("trace_id","11111122222222332")
    #     instance: Agent = AgentManager().get_instance_obj('demo_rag_agent')
    #     output_object: OutputObject = instance.run(input='分析下巴菲特减持比亚迪的原因')
    #     res_info = f"\nRag agent execution result is :\n"
    #     res_info += output_object.get_data('output')
    #     print(res_info)
    #     time.sleep(10)


if __name__ == '__main__':
    unittest.main()
