# !/usr/bin/env python3
# -*- coding:utf-8 -*-
from langchain_core.utils.json import parse_json_markdown

# @Time    : 2024/6/11 09:49
# @Author  : weizjajj 
# @Email   : weizhongjie.wzj@antgroup.com
# @FileName: simple_math_tool.py


from agentuniverse.agent.action.tool.tool import Tool


class AddTool(Tool):
    def execute(self, input_params, **kwargs):
        a, b = input_params.split(',')
        result = float(a) + float(b)
        return result


class SubtractTool(Tool):
    def execute(self, input_params, **kwargs):
        a, b = input_params.split(',')
        result = float(a) - float(b)
        return result


class MultiplyTool(Tool):
    def execute(self, input_params, **kwargs):
        a, b = input_params.split(',')
        result = float(a) * float(b)
        return result


class DivideTool(Tool):
    def execute(self, input_params, **kwargs):
        a, b = input_params.split(',')
        result = float(a) / float(b)
        return result
