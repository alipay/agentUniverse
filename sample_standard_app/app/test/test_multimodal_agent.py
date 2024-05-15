# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/5/15 17:37
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: test_multimodal_agent.py
import unittest

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.base.agentuniverse import AgentUniverse


class MultimodalAgentTest(unittest.TestCase):
    """
    Test cases for the multimodal agent
    """

    def setUp(self) -> None:
        AgentUniverse().start(config_path='../../config/config.toml')

    def test_multimodal_agent(self):
        """Test demo multimodal agent."""
        instance: Agent = AgentManager().get_instance_obj('demo_multimodal_agent')
        output_object: OutputObject = instance.run(input='图片里有什么东西，具体是哪个城市的景色，请仔细描述下',
                                                   image_url='https://cdn.pixabay.com/photo/2016/03/27/00/01/australia-1281935_1280.jpg')
        res_info = f"\nMultimodal agent execution result is :\n"
        res_info += output_object.get_data('output')
        print(res_info)


if __name__ == '__main__':
    unittest.main()
