#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time   : 2024/7/18 14:43
# @Author : fluchw
# @Email  : zerozed00@qq.com
# @File   ：court_service.py
from typing import Dict, List, Any

from agentuniverse.agent_serve.service import Service
from agentuniverse.base.util.logging.logging_util import LOGGER


class drama_service(Service):
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

    def run(self, **kwargs) -> dict:
        user_id = kwargs.get('user_id')
        if not user_id:
            return {'message': '没有用户id,请检查'}
        LOGGER.info(f"kwargs {kwargs}")
        # 获取或生成 session_id
        # if 'session_id' not in session:
        #     session['session_id'] = str(uuid.uuid4())
        session_id = kwargs.get('session_id')
        # kwargs['session_id'] = session_id

        # 获取用户和聊天记录的历史数据
        history_key = f"{user_id}_{session_id}"
        if history_key not in self.chat_history:
            self.chat_history[history_key] = []

        # 传递历史数据到 agent
        kwargs['chat_history'] = self.chat_history[history_key]
        LOGGER.debug(f"self.chat_history {self.chat_history}")
        LOGGER.debug(f"kwargs['chat_history'] {kwargs['chat_history']}")
        redata = self.agent.run(**kwargs)
        LOGGER.debug(f"re service {redata}")

        rsp = redata.to_dict()
        LOGGER.debug(f"rsp {rsp}")
        LOGGER.debug(f'rsp["chat_history"] {rsp["chat_history"]}')

        # 更新聊天记录
        self.chat_history[history_key] = rsp["chat_history"]
        LOGGER.debug(f"ser chat_history {self.chat_history}")
        msg = {
            'cur_drama': {
                'noed': rsp['cur_node'],
                'role': rsp['role'],
                'action': rsp['action']
            },
            'drama': rsp['drama'],
            'user_id': user_id,
            'session_id': session_id,
            "role": rsp['role'],
            "content": rsp['output'],
        }
        LOGGER.info(f"msg {msg}")
        LOGGER.info(f"user_id {user_id}")
        LOGGER.info(f"session_id {session_id}")
        return msg
