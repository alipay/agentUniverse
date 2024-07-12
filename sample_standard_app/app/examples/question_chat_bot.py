#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time   : 2024/6/22 15:07
# @Author : fluchw
# @Email  : zerozed00@qq.com
# @File   ：question_chat_bot.py
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.base.agentuniverse import AgentUniverse
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager

AgentUniverse().start(config_path='../../config/config.toml')


def chat(question: str):
    """ Peer agents example.

    The peer agents in agentUniverse become a chatbot and can ask questions to get the answer.
    """
    # instance: Agent = AgentManager().get_instance_obj('demo_planning_agent')
    # instance.run(input=question)
    instance: Agent = AgentManager().get_instance_obj('question_classification_agent')
    output_object: OutputObject = instance.run(input=question)
    res_info = f"\nPlanning agent execution result is :\n"
    # for index, one_framework in enumerate(output_object.get_data('framework')):
    #     res_info += f"[{index + 1}] {one_framework} \n"
    # print(res_info)
    print(output_object)

if __name__ == '__main__':
    chat("请问批发业注册资本最高的前3家公司的名称以及他们的注册资本（单位为万元）？")