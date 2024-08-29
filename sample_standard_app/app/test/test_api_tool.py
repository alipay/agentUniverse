import os
import unittest

from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.agentuniverse import AgentUniverse


class SearchToolTest(unittest.TestCase):
    """
    Test cases for the rag agent
    """

    def setUp(self) -> None:
        AgentUniverse().start(config_path='../../config/config.toml')

    def test_api_tool(self):
        """Test demo rag agent."""
        res = ToolManager().get_instance_obj("test_plugin_arxiv").run(search_query="查找deep learning 相关论文")
        print('论文查询',res)


if __name__ == '__main__':
    unittest.main()
