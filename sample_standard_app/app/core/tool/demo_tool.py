# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/31 11:00
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: demo_tool.py
from langchain_community.utilities.google_serper import GoogleSerperAPIWrapper
from agentuniverse.agent.action.tool.tool import Tool, ToolInput


class DemoTool(Tool):
    """The demo tool.

    Implement the execute method of demo tool, using the `GoogleSerperAPIWrapper` to implement a simple Google search.

    Note:
        You need to sign up for a free account at https://serper.dev and get the serpher api key (2500 free queries).
    """

    def execute(self, tool_input: ToolInput):
        query = tool_input.get_data("input")
        # get top3 results from Google search.
        search = GoogleSerperAPIWrapper(k=3, type="search")
        return search.run(query=query)
