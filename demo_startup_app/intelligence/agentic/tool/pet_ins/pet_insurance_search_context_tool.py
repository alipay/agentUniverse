# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/11/12 11:59
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: search_context_tool.py
import json

import requests

from agentuniverse.agent.action.tool.tool import Tool, ToolInput
from agentuniverse.base.util.logging.logging_util import LOGGER

PRE_API_URL = "https://fincopilotcore.antgroup-inc.cn/api/copilot/runMxc/faq"


class SearchContextTool(Tool):

    def execute(self, tool_input: ToolInput):
        question = tool_input.get_data('input')
        try:
            headers = {
                "Content-Type": "application/json",
                "x-fincopilotcore-signature": "LmHJoTYJxDh3yq@2dQ",
            }
            # 要发送的数据
            data = {
                "chatId": "6bc634d8dbf049feb9b64c91e35832fc-c",
                "sessionId": "e5cdeb076d5b40eda74071e8d33c3594-s",
                "userId": "2088942002730533",
                "sceneCode": "ant_fortune_insurance_property",
                "query": question,
                "decoderType": "ins_slot_v2",
                "inputMethod": "user_input",
                "userInfoMap": {
                    "userId": "2088942002730533",
                    "consultantSceneCode": "ant_fortune_insurance_property",
                    "spNo": "36763",
                    "prodNo": "36763",
                },
                "enterScene": {
                    "sceneCode": "ant_fortune_insurance_property",
                    "productNo": "36763",
                }
            }
            top_k = tool_input.get_data('top_k') if tool_input.get_data('top_k') else 2
            LOGGER.info(f"search context tool input: {data}")
            response = requests.post(PRE_API_URL, headers=headers, data=json.dumps(data, ensure_ascii=False))
            result = response.json()['result']
            recallResultTuples = result.get('recallResultTuples')

            context = f"提出的问题是:{question}\n\n这个问题检索到的答案相关内容是:\n\n"
            index = 0
            for recallResult in recallResultTuples:
                if index == top_k:
                    return context
                if recallResult.get('content'):
                    context += (f"knowledgeTitle: {recallResult.get('knowledgeTitle')}\n"
                                f"knowledgeContent: {recallResult.get('content')}\n\n")
                    index += 1
            return context
        except Exception as e:
            LOGGER.error(f"invoke search context tool failed: {str(e)}")
            raise e


def main():
    tool = SearchContextTool()
    tool_input_dict = {
        "input": "宠物医保投保对宠物年龄的要求是多少？"
    }
    response = tool.run(**tool_input_dict)
    print(response)


if __name__ == '__main__':
    main()
