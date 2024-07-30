# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/29 12:14
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: yaml_util.py
from ruamel.yaml import YAML


def update_nested_yaml_value(config_path, updates):
    yaml = YAML()
    # read an existing YAML file
    with open(config_path, 'r', encoding='utf-8') as file:
        config_data = yaml.load(file)

    # batch update the value of the target key
    for path, new_value in updates.items():
        keys = path.split('.')
        d = config_data
        for key in keys[:-1]:
            d = d[key]
        # modify the value of the target key
        d[keys[-1]] = new_value

    # write the modified content back to the YAML file
    with open(config_path, 'w', encoding='utf-8') as file:
        yaml.dump(config_data, file)
