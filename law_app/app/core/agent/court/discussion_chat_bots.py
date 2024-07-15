# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/7 11:22
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: discussion_chat_bots.py
from agentuniverse.base.agentuniverse import AgentUniverse
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager

AgentUniverse().start(config_path='../../law_config/law_config.toml')


def chat(question: str,background:str):
    instance: Agent = AgentManager().get_instance_obj('court_host_agent')
    instance.run(input=question,background = background)


if __name__ == '__main__':
    input = ''
    background=''

    chat(input,background)
