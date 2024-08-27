# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/29 12:14
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: yaml_util.py
import os

from ruamel.yaml import YAML


def update_nested_yaml_value(config_path: str, updates: dict) -> None:
    """Update nested values in YAML

    Args:
        config_path(str): The path to the YAML file.

        updates(dict): A dictionary of key-value pairs to update in the YAML file.
        The keys should be dot-separated paths to the target values,
        and the values should be the new values to set.

    Examples:
        update_nested_yaml_value(
        config_path='/xxx/agentUniverse/sample_standard_app/app/core/agent/rag_agent_case/demo_rag_agent.yaml',
        updates={'info.description': 'demo rag agent',
          'profile.llm_model.name': 'qwen_llm',
          'profile.llm_model.temperature': 0.5,
           'profile.llm_model.model_name': 'qwen2-72b-instruct',
           'action.tool': ['google_search_tool']
           })
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
            # modify the value of the target key
            d[keys[-1]] = new_value
        except Exception as e:
            print(f"Skipping update for '{path}': {e}")

    # write the modified content back to the YAML file
    with open(config_path, 'w', encoding='utf-8') as file:
        yaml.dump(config_data, file)


def write_yaml_file(file_path, config_data) -> None:
    """Writes the dictionary to a YAML file with the specified file path.
    
    Args:
        file_path (str): The path to the YAML file.
        config_data (dict): The dictionary to write to the YAML file.
    """
    yaml = YAML()
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Write the dictionary to the YAML file
    with open(file_path, 'w') as yaml_file:
        yaml.dump(config_data, yaml_file)
