# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/29 12:14
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: yaml_util.py
from ruamel.yaml import YAML


def update_nested_yaml_value(config_path, updates) -> None:
    """Update nested values in YAML

    Args:
        config_path(str): The path to the YAML file.

        updates(dict): A dictionary of key-value pairs to update in the YAML file.
        The keys should be dot-separated paths to the target values,
        and the values should be the new values to set.
    """
    yaml = YAML()
    # read an existing YAML file
    with open(config_path, 'r', encoding='utf-8') as file:
        config_data = yaml.load(file)

    # batch update the value of the target key
    for path, new_value in updates.items():
        keys = path.split('.')
        d = config_data
        try:
            for key in keys[:-1]:
                if key not in d:
                    raise KeyError(f"Key '{key}' not found in the configuration")
                d = d[key]
            if keys[-1] in d:
                # modify the value of the target key
                d[keys[-1]] = new_value
        except Exception as e:
            print(f"Skipping update for '{path}': {e}")

    # write the modified content back to the YAML file
    with open(config_path, 'w', encoding='utf-8') as file:
        yaml.dump(config_data, file)
