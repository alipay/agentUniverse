#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time   : 2024/7/18 14:43
# @Author : fluchw
# @Email  : zerozed00@qq.com
# @File   ：court_service.py
import uuid
from typing import Dict, List, Any

from flask import jsonify

from agentuniverse.agent_serve.service import Service
from agentuniverse.base.util.logging.logging_util import LOGGER


class game_service(Service):
    """
    第一轮输入:
    {
    "service_id": "court_service",
    "params": {
        "user_id":"1984",
        "input":"",
        "background":"李明诉王芳欠款纠纷案。2019年3月，李明借给王芳10万元人民币，约定一年后归还。双方没有签订书面借款合同，但有微信聊天记录为证。到2020年3月归还期限到期后，王芳以各种理由推脱，至今未归还借款。李明多次催促未果，遂向法院提起诉讼，要求王芳归还借款10万元并支付相应的利息。"
        }
    }

    第二轮输入:
    {
    "service_id": "court_service",
    "params": {
        "user_id":"1984",
        "chat_id":"347b6394-4e0d-47fd-9c2e-cfc9036bf2d1",
        "input":"快还钱"
        }
    }
    """
    chat_history: Dict[str, List[Dict[str, Any]]] = {}

    def run(self, **kwargs) -> str:
        """The executed function when the service is called."""
        user_id = kwargs.get('user_id')
        chat_id = kwargs.get('chat_id')

        if not user_id:
            return jsonify({'message':'没有用户id,请检查'}), 200

        # 如果没有传入会话ID，则生成一个新的会话ID
        if not chat_id:
            chat_id = str(uuid.uuid4())
            kwargs['chat_id'] = chat_id

        # 获取用户和聊天记录的历史数据
        history_key = f"{user_id}_{chat_id}"
        if history_key not in self.chat_history:
            self.chat_history[history_key] = []

        # 传递历史数据到agent
        kwargs['chat_history'] = self.chat_history[history_key]
        LOGGER.debug(f"kwargs['chat_history'] {kwargs['chat_history']}")
        redata = self.agent.run(**kwargs)
        LOGGER.debug(f"re service {redata}")

        for data in redata:
            rsp = data.to_dict()
            LOGGER.debug(f"rsp {rsp}")

            # 更新聊天记录
            self.chat_history[history_key].append({
                'agent_name': rsp['agent_name'],
                "type": rsp['type'],
                'content': rsp['output']
            })
            LOGGER.debug(f"ser chat_history {self.chat_history}")
            msg = {
                'user_id': user_id,
                'chat_id': chat_id,
                "agent_name": rsp['agent_name'],
                "type":rsp['type'],
                "content": rsp['output'],
            }
            LOGGER.info(f"msg {msg}")
            LOGGER.info(f"user_id {user_id}")
            LOGGER.info(f"chat_id {chat_id}")
            yield msg

        # # 返回新的会话ID
        # if not kwargs.get('chat_id'):
        #     yield json.dumps({'chat_id': chat_id})
