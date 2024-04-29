# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/4/28 14:44
# @Author  : weizjajj
# @Email   : weizhongjie.wzj@antgroup.com
# @FileName: map_planner.py

from typing import List

from agentuniverse.agent.action.knowledge.knowledge import Knowledge
from agentuniverse.agent.action.knowledge.knowledge_manager import KnowledgeManager
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.agent_model import AgentModel
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.plan.planner.planner import Planner


class MapReducePlanner(Planner):
    """
    Map planner.
    """

    def invoke(self, agent_model: AgentModel, planner_input: dict,
               input_object: InputObject) -> dict:
        """Invoke the planner.

        Args:
            agent_model (AgentModel): Agent model object.
            planner_input (dict): Planner input object.
            input_object (InputObject): Agent input object.
        Returns:
            dict: The planner result.
        """
        # load docs to map
        docs = self.load_docs(agent_model, input_object)
        # load map agent
        map_agent_name = agent_model.profile.get('map_agent')
        # load reduce(rag) agent
        reduce_agent_name = agent_model.profile.get('reduce_agent')
        # load agent
        if not map_agent_name or not reduce_agent_name:
            raise Exception("MapReducePlanner need map_agent and reduce_agent")
        map_agent = AgentManager().get_instance_obj(map_agent_name)
        reduce_agent = AgentManager().get_instance_obj(reduce_agent_name)
        if not map_agent or not reduce_agent:
            raise Exception("MapReducePlanner need map_agent and reduce_agent")

        reduce_input = planner_input.copy()
        # not have docs roll back to reduce (only rag)
        if len(docs) > 0:
            map_input = planner_input.copy()
            map_input['docs'] = docs
            map_result = map_agent.run(**map_input)
            if not reduce_input.get('background'):
                reduce_input['background'] = map_result.get_data('output')
            else:
                reduce_input['background'] = reduce_input['background'] + map_result.get_data('output')
        # do reduce(rag)
        reduce_result = reduce_agent.run(**reduce_input)
        return reduce_result.to_dict()

    def load_docs(self, agent_model: AgentModel, input_object: InputObject) -> List[Document]:
        """Tool or knowledge processing.

        Args:
            agent_model (AgentModel): Agent model object.
            planner_input (dict): Planner input object.
            input_object (InputObject): Agent input object.
        """
        action: dict = agent_model.action or dict()
        tools: list = action.get('tool') or list()
        knowledge: list = action.get('knowledge') or list()

        action_result: list = list()

        for tool_name in tools:
            tool = ToolManager().get_instance_obj(tool_name)
            if tool is None:
                continue
            tool_input = {key: input_object.get_data(key) for key in tool.input_keys}
            doc = tool.run(**tool_input)
            if type(doc) is str:
                doc = Document(text=doc, metadata={})
            action_result.append(doc)
        for knowledge_name in knowledge:
            knowledge: Knowledge = KnowledgeManager().get_instance_obj(knowledge_name)
            if knowledge is None:
                continue
            knowledge_res: List[Document] = knowledge.store.query(
                Query(query_str=input_object.get_data(self.input_key), similarity_top_k=2), **input_object.to_dict())
            for document in knowledge_res:
                action_result.append(document.text)
        if input_object.get_data('docs'):
            if type(input_object.get_data('docs')) is str:
                action_result.append(Document(text=input_object.get_data('docs'), metadata={}))
            elif type(input_object.get_data('docs')) is list:
                action_result.extend(input_object.get_data('docs'))
        return action_result
