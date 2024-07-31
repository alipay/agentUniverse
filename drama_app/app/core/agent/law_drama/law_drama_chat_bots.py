# !/usr/bin/env python3
# -*- coding:utf-8 -*-

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
# @Time    : 2024/6/7 11:22
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: discussion_chat_bots.py
from agentuniverse.base.agentuniverse import AgentUniverse

AgentUniverse().start(config_path='../../../../drama_config/drama_config.toml')


def chat(**kwargs):
    # instance: Agent = AgentManager().get_instance_obj('drama_host_agent')
    instance: Agent = AgentManager().get_instance_obj('law_drama_agent')

    instance.run(**kwargs)


if __name__ == '__main__':
    """
        {
        "service_id": "drama_service",
        "params": {
            "user_role":"原告方",
            "user_id":"1984",
            "input":"",
            "cur_node":"a0",
            "background":"李明诉王芳欠款纠纷案。2019年3月，李明借给王芳10万元人民币，约定一年后归还。双方没有签订书面借款合同，但有微信聊天记录为证。到2020年3月归还期限到期后，王芳以各种理由推脱，至今未归还借款。李明多次催促未果，遂向法院提起诉讼，要求王芳归还借款10万元并支付相应的利息。"
            }
        }
    """

    dramas = {

        "a0": {"role": "法官", "action": "开庭", "next": "a1", "type": "normal"},
        "a1": {"role": "原告方", "action": "陈述", "next": "a2", "type": "normal"},
        "a2": {"role": "审判员", "action": "判断原告方的陈述是否与当前背景有关", "next": {"选择重新描述": "a1", "选择继续": "a3"},
               "type": "branch"},
        "a3": {"role": "被告方", "action": "陈述", "next": "a4", "type": "normal"},
        "a4": {"role": "审判员", "action": "判断被告方的陈述是否与当前背景有关", "next": {"选择重新描述": "a3", "选择继续": "a5"},
               "type": "branch"},
        "a5": {"role": "原告方", "action": "陈述", "next": "a6", "type": "normal"},
        "a6": {"role": "法官", "action": "提出让双方互相提问", "next": "b0", "type": "normal"},

        # "b0": {"role": "原告方", "action": "原告向被告提问", "next": "b1", "type": "normal"},
        # "b1": {"role": "被告方", "action": "被告选择回答或者不回答", "next": {"选择回答": "b2", "选择不回答": "b4"},
        #        "type": "branch"},
        # "b2": {"role": "原告方", "action": "原告向合议庭提交数据进行明示", "next": "b3", "type": "normal"},
        # "b3": {"role": "被告方", "action": "被告选择回答或者不回答", "next": {"选择回答": "b2", "选择不回答": "b4"},
        #        "type": "branch"},
        # "b4": {"role": "被告方", "action": "被告向原告提问", "next": "b5", "type": "normal"},
        # "b5": {"role": "原告方", "action": "原告回答", "next": "b6", "type": "normal"},
        # "b6": {"role": "法官", "action": "双方没有问题了吧", "next": {"有问题": "b0", "没问题": "c0"}, "type": "normal"},
        #
        # "c0": {"role": "法官", "action": "下面进行法庭辩论,绕着三个焦点进行辩论", "next": "c1", "type": "normal"},
        #
        # "c1": {"role": "原告方", "action": "原告对三个焦点进行辩论", "next": "c2", "type": "normal"},
        # "c2": {"role": "被告方", "action": "被告对三个焦点进行辩论", "next": "c3", "type": "normal"},
        #
        # "c3": {"role": "法官", "action": "原告要不要发表第二轮辩论意见", "next": "c1", "type": "normal"},
        #
        # "c4": {"role": "原告方", "action": "原告对被告的输出进行辩论", "next": "c5", "type": "normal"},
        # "c5": {"role": "法官", "action": "判决", "next": "d0", "type": "normal"},
        #
        # "d0": {"role": "法官", "action": "判决", "next": None, "type": "normal"}

    }

    data = {
        "user_role": "原告方",
        "input": "还钱",
        "cur_node":"a0",
        # "dramas":dramas,
        "background": "李明诉王芳欠款纠纷案。2019年3月，李明借给王芳10万元人民币，约定一年后归还。双方没有签订书面借款合同，但有微信聊天记录为证。到2020年3月归还期限到期后，王芳以各种理由推脱，至今未归还借款。李明多次催促未果，遂向法院提起诉讼，要求王芳归还借款10万元并支付相应的利息。"
    }

    chat(**data)
