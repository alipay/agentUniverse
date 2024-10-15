# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/10/14 14:59
# @Author  : weizjajj
# @Email   : weizhongjie.wzj@antgroup.com
# @FileName: framework_matching_tool.py

from agentuniverse.agent.action.tool.tool import Tool, ToolInput
import pandas as pd
from pydantic import BaseModel


class FrameWorkInfo(BaseModel):
    product_track: str
    interpret_latitude: str
    argument_direction: str
    argument_direction_list: list
    expression_techniques: str


class LoadFrameWorkTool(Tool):
    def execute(self, tool_input: ToolInput):
        framework_path = tool_input.get_data("framework_path")

        # 从csv文件中读取信息
        df = pd.read_csv(framework_path, header=0)
        values = df.values.tolist()
        frameworks = []
        for row in values:
            framework_info = FrameWorkInfo(
                product_track=row[0],
                interpret_latitude=row[1],
                argument_direction=row[2],
                argument_direction_list=row[3][1:len(row[3]) - 1].split(","),
                expression_techniques=row[4]
            )
            frameworks.append(framework_info.model_dump())

        return {"frameworks": frameworks}


class FrameworkMatchingTool(Tool):

    def execute(self, tool_input: ToolInput):
        frameworks = tool_input.get_data("frameworks")
        fund_info = tool_input.get_data("fund_info")

        # 获取基金经理的管理年限
        manager_age = fund_info["manager_age"]
