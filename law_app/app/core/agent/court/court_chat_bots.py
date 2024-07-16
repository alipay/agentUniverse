# !/usr/bin/env python3
# -*- coding:utf-8 -*-

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
# @Time    : 2024/6/7 11:22
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: discussion_chat_bots.py
from agentuniverse.base.agentuniverse import AgentUniverse

AgentUniverse().start(config_path='../../../../law_config/law_config.toml')


def chat(question: str, background: str):
    instance: Agent = AgentManager().get_instance_obj('court_host_agent')
    instance.run(input=question, background=background)


if __name__ == '__main__':
    input = '李明诉王芳欠款纠纷案。2019年3月，李明借给王芳10万元人民币，约定一年后归还。双方没有签订书面借款合同，但有微信聊天记录为证。到2020年3月归还期限到期后，王芳以各种理由推脱，至今未归还借款。李明多次催促未果，遂向法院提起诉讼，要求王芳归还借款10万元并支付相应的利息。'
    background = ''

    chat(input, background)
