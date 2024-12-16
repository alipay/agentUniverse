# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/03 19:10
# @Author  : xutingdong
# @Email   : xutingdong.xtd@antgroup.com
# @FileName: gen_image_tool.py

from agentuniverse.agent.action.tool.tool import Tool, ToolInput
from PIL import Image
import requests
import io
from urllib import request, parse
import urllib.parse


class GenImageTool(Tool):
    """The mock search tool.

    In this tool, we mocked the search engine's answers to search for information about BYD and Warren Buffett.

    Note:
        The tool is only suitable for users searching for Buffett or BYD related queries.
        We recommend that you configure your `SERPER_API_KEY` and use google_search_tool to get information.
    """

    def execute(self, tool_input: ToolInput):
        input = tool_input.get_data("input")
        """Demonstrates the execute method of the Tool class."""
        input = parse.quote(input, safe='/')
        image_url = f'https://image.pollinations.ai/prompt/{input}'
        # url_request = request.Request(image_url)
        # url_response = request.urlopen(url_request)
        # data = url_response.read()
        # path = 'test.jpg'
        # with open(path, 'wb') as f:
        #     f.write(data)

        response = requests.get(image_url)
        if response.status_code == 200:
            image = Image.open(io.BytesIO(response.content))
            image.show()
        else:
            print("图片生成失败")
