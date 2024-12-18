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

PRE_API_URL = "xxxx"


class SearchContextTool(Tool):

    def execute(self, tool_input: ToolInput):
        question = tool_input.get_data('input')
        try:
            headers = {
                "Content-Type": "application/json"
            }
            # 要发送的数据
            data = {
                "chatId": "xxxx",
                "sessionId": "xxxx",
                "userId": "xxxxx",
                "sceneCode": "xxxx",
                "query": question,
                "decoderType": "xxxx",
                "inputMethod": "user_input",
                "enterScene": {
                    "sceneCode": "xxx",
                    "productNo": "xxxx",
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