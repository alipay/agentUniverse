# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/11 20:52
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: dispatch.py
import yaml

from agentuniverse.base.util.logging.logging_util import LOGGER
from agentuniverse.base.agentuniverse import AgentUniverse

from agentuniverse_dataflow.flow.dataflow import Dataflow

AgentUniverse().start(config_path='../../config/config.toml')


def load_dataflows_from_yaml(conf_file):
    with open(conf_file, 'r') as file:
        config = yaml.safe_load(file)
    dataflows = []
    yaml_list = config.get('dataflows')
    for item in yaml_list:
        dataflows.append(Dataflow(item))
    return dataflows


def dispatch(conf_file='dispatch.yaml'):
    dataflows = load_dataflows_from_yaml(conf_file)
    try:
        for dataflow in dataflows:
            dataflow.execute()
    except Exception as e:
        LOGGER.error(f"An error occurred: {e}")


if __name__ == '__main__':
    dispatch('dispatch.yaml')
