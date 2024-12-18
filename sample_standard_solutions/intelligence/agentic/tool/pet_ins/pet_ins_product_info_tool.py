# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/11/12 11:59
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: search_context_tool.py
from agentuniverse.agent.action.tool.tool import Tool, ToolInput
from sample_standard_solutions.intelligence.utils.constant import product_b_info, product_c_info


class SearchProductInfoTool(Tool):

    def execute(self, tool_input: ToolInput):
        product_info_item_list = tool_input.get_data('input')

        product_b_description = product_b_info.BASE_PRODUCT_DESCRIPTION
        product_c_description = product_c_info.BASE_PRODUCT_DESCRIPTION
        for item in product_info_item_list:
            if item == 'G':
                continue
            if item == 'K':
                product_b_description += product_b_info.PRODUCT_DESCRIPTION_MAP.get('L')
                product_c_description += product_c_info.PRODUCT_DESCRIPTION_MAP.get('L')
            else:
                product_b_description += product_b_info.PRODUCT_DESCRIPTION_MAP.get(item)
                product_c_description += product_c_info.PRODUCT_DESCRIPTION_MAP.get(item)

        return {'B': product_b_description, 'C': product_c_description}
