# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/5/8 11:41
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: peer_chat_bot.py
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.base.agentuniverse import AgentUniverse
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.base.util.logging.logging_util import LOGGER

AgentUniverse().start(config_path='../../config/config.toml')


def chat(question: str):
    """ Peer agents example.

    The peer agents in agentUniverse become a chatbot and can ask questions to get the answer.
    """
    # instance: Agent = AgentManager().get_instance_obj('demo_planning_agent')
    # instance.run(input=question)
    instance: Agent = AgentManager().get_instance_obj('my_planning_agent')
    output_object: OutputObject = instance.run(input=question)
    res_info = f"\nPlanning agent execution result is :\n"
    # for index, one_framework in enumerate(output_object.get_data('framework')):
    #     res_info += f"[{index + 1}] {one_framework} \n"
    # print(res_info)
    LOGGER.debug(output_object)

if __name__ == '__main__':
    chat("请问批发业注册资本最高的前3家公司的名称以及他们的注册资本（单位为万元）？")
    # chat("帮我分析下2023年巴菲特减持比亚迪原因")
