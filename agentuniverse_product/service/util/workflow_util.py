# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/23 16:24
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: workflow_util.py
import os

from agentuniverse.base.component.component_configer_util import ComponentConfigerUtil
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.component_configer.configers.workflow_configer import WorkflowConfiger
from agentuniverse.base.config.configer import Configer
from agentuniverse.workflow.workflow import Workflow
from agentuniverse.workflow.workflow_manager import WorkflowManager


def register_workflow(file_path: str):
    """Register a workflow instance to the workflow manager.

    Args:
        file_path (str): The path to the specific workflow configuration file.
    """
    absolute_file_path = os.path.abspath(file_path)
    configer = Configer(path=absolute_file_path).load()
    component_configer = ComponentConfiger().load_by_configer(configer)
    workflow_configer: WorkflowConfiger = WorkflowConfiger().load_by_configer(component_configer.configer)
    component_clz = ComponentConfigerUtil.get_component_object_clz_by_component_configer(workflow_configer)
    workflow: Workflow = component_clz().initialize_by_component_configer(workflow_configer)
    workflow.component_config_path = component_configer.configer.path
    WorkflowManager().register(workflow.get_instance_code(), workflow)
