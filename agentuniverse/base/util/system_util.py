# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/14 10:42
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: system_util.py

from pathlib import Path

PROJECT_ROOT_PATH = None


def get_project_root_path() -> Path:
    """Get the project root path."""
    global PROJECT_ROOT_PATH
    if PROJECT_ROOT_PATH:
        return PROJECT_ROOT_PATH
    current_work_directory = Path.cwd()
    if current_work_directory.name != 'bootstrap':
        print(f"Warn: Boot file is not located under directory 'bootstrap', "
              f"but under '{current_work_directory.name}'")

    root_path = current_work_directory.parents[1]
    PROJECT_ROOT_PATH = root_path
    return root_path
