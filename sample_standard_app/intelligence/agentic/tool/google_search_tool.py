# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/3/31 11:00
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: google_search_tool.py
from typing import Optional

from pydantic import Field
from langchain_community.utilities.google_serper import GoogleSerperAPIWrapper
from agentuniverse.agent.action.tool.tool import Tool, ToolInput
from agentuniverse.base.util.env_util import get_from_env

from sample_standard_app.intelligence.agentic.tool.mock_search_tool import MockSearchTool


class GoogleSearchTool(Tool):
    """The demo google search tool.

    Implement the execute method of demo google search tool, using the `GoogleSerperAPIWrapper` to implement a simple Google search.

    Note:
        You need to sign up for a free account at https://serper.dev and get the serpher api key (2500 free queries).
    """

    serper_api_key: Optional[str] = Field(default_factory=lambda: get_from_env("SERPER_API_KEY"))

    def execute(self, tool_input: ToolInput):
        input = tool_input.get_data("input")
        if self.serper_api_key is None:
            return MockSearchTool().execute(tool_input=tool_input)
        # get top10 results from Google search.
        search = GoogleSerperAPIWrapper(serper_api_key=self.serper_api_key, k=10, gl="us", hl="en", type="search")
        return search.run(query=input)