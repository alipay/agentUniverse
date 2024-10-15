# !/usr/bin/env python3
# -*- coding:utf-8 -*-
from datetime import datetime

from agentuniverse.agent.action.tool.tool import Tool, ToolInput


# @Time    : 2024/10/14 14:59
# @Author  : weizjajj 
# @Email   : weizhongjie.wzj@antgroup.com
# @FileName: framework_matching_tool.py


class FrameworkMatchingTool(Tool):

    def execute(self, tool_input: ToolInput):
        frameworks = tool_input.get_data("frameworks")
        fund_info = tool_input.get_data("fund_info")

        # 1. 匹配赛道
        track_list = [
            # "成长风格",
            # "均衡风格",
            # "科技行业",
            # "消费行业"
        ]
        for framework in frameworks:
            if framework.get("product_track") not in track_list:
                track_list.append(framework.get("product_track"))

        # 2. 匹配投资方向

        # "manager_info": {{
        #     "name": "基金经理姓名",
        #     "date": "基金经理的入职时间",
        #     "description": "基金经理简介"
        # }},
        manager_info = fund_info.get("manager_info")
        manager_date = manager_info.get("date")

        date = datetime.strptime(manager_date, "%Y-%m-%d")

        argument_direction_list = []

        # 截止到今天有多少天
        days = (datetime.now() - date).days
        if days < 365:
            argument_direction = "基金经理任职经验过短"
            argument_direction_list.append(argument_direction)

        # "base_income_info": {{
        #     "last_week": "近一周收益率",
        #     "last_month": "近一月收益率",
        #     "last_three_moth": "近三个月收益率",
        #     "last_six_moth": "近了六个月收益率",
        #     "this_year": "今年以来收益率",
        #     "last_year": "近一年收益率"
        # }},

        count = 0
        for key, value in fund_info.get("base_income_info").items():
            if float(value) > 0:
                count += 1

        if count >= 4:
            argument_direction = "基金经理收益率过低"
            argument_direction_list.append(argument_direction)
