# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/2 16:58
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: data_agent.py
from agentuniverse.base.agentuniverse import AgentUniverse
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager

AgentUniverse().start(config_path='../../config/config.toml')


def data_process(dataset_path: str, turn: int, **kwargs):
    instance: Agent = AgentManager().get_instance_obj('data_agent')
    instance.run(dataset_path=dataset_path, turn=turn, **kwargs)


if __name__ == '__main__':
    data_process(dataset_path="./data/query.jsonl", turn=1)
