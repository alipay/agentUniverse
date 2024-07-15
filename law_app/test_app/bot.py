#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time   : 2024/7/10 9:32
# @Author : fluchw
# @Email  : zerozed00@qq.com
# @File   ：bot.py
import os

from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.base.agentuniverse import AgentUniverse
from agentuniverse.base.util.logging.logging_util import LOGGER
import sys
# print(sys.path)
# relative_path='../../../../config/config.toml'
# absolute_path = os.path.abspath(relative_path)
# LOGGER.debug(f'{relative_path} -> {absolute_path}')

# with open(absolute_path, 'r', encoding='utf-8') as file:
#     content = file.read()
#     print(content)


# AgentUniverse().start(config_path=absolute_path)
AgentUniverse().start("../../config/config.toml")
# C:\Users\wuss\Desktop\xuexi\python\agentUniverse\sample_standard_app\app\examples\question_chat_bot.py
# C:\Users\wuss\Desktop\xuexi\python\agentUniverse\sample_standard_app\app\core\agent\law_agent_case\bot.py
def chat(question: str):
    """ Rag agent example.

    The rag agent in agentUniverse becomes a chatbot and can ask questions to get the answer.
    """

    # 加载名字为law_rag_agent的agent
    instance: Agent = AgentManager().get_instance_obj('test_agent')
    LOGGER.debug(f"instance {instance}")

    # 运行agent
    output_object: OutputObject = instance.run(input=question)
    LOGGER.debug(f"output_object.to_dict() {output_object.to_dict()}")

    # question = f"\nYour event is :\n"
    # question += output_object.get_data('input')
    # LOGGER.debug(f"question {question}")
    #
    # background_info = f"\nRetrieved background is :\n"
    # # LOGGER.debug(f"background {output_object.get_data('background').replace('\n','')}")
    # background_info += output_object.get_data('background').replace("\n","")
    # LOGGER.debug(f"background_info {background_info}")

    res_info = f"\nRag chat bot execution result is :\n"
    res_info += output_object.get_data('output')
    LOGGER.debug(f"res_info {res_info}")
    # print(res_info)


if __name__ == '__main__':
    LOGGER.debug("测试bot↓")
    chat("广州哪里好玩")
    LOGGER.debug("测试bot↑")
