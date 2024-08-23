# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/23 15:35
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: workflow_planner.py
from agentuniverse.agent.agent_model import AgentModel
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.plan.planner.planner import Planner
from agentuniverse.workflow.workflow import Workflow
from agentuniverse.workflow.workflow_manager import WorkflowManager


class WorkflowPlanner(Planner):
    """Workflow planner class."""

    def invoke(self, agent_model: AgentModel, planner_input: dict, input_object: InputObject) -> dict:
        """Invoke the planner.

        Args:
            agent_model (AgentModel): Agent model object.
            planner_input (dict): Planner input object.
            input_object (InputObject): The input parameters passed by the user.
        Returns:
            dict: The planner result.
        """
        planner = agent_model.plan.get('planner', {})
        workflow_id = planner.get('workflow_id')
        workflow: Workflow = WorkflowManager().get_instance_obj(component_instance_name=workflow_id)
        workflow.run()
        return {}
