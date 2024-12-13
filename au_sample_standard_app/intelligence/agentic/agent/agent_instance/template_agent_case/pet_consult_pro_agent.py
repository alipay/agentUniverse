# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/12/12 22:59
# @Author  : jijiawei
# @Email   : jijiawei.jjw@antgroup.com
# @FileName: pet_consult_agent_pro.py
import json

from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.base.util.agent_util import assemble_memory_output
from agentuniverse.base.util.prompt_util import process_llm_token
from agentuniverse.llm.llm import LLM
from agentuniverse.prompt.prompt import Prompt
from langchain_core.output_parsers import StrOutputParser

from au_sample_standard_app.intelligence.agentic.agent.agent_template.pet_agent_template import \
    PetRagAgentTemplate


class PetInsuranceConsultProAgent(PetRagAgentTemplate):

    def customized_execute(self, input_object: InputObject, agent_input: dict, memory: Memory, llm: LLM, prompt: Prompt,
                           **kwargs) -> dict:
        # 改写问题
        detail_tool = ToolManager().get_instance_obj('pet_insurance_info_tool')
        tool_res = detail_tool.run(query='宠物医保')
        agent_input['prod_description'] = tool_res
        rewrite_agent: Agent = AgentManager().get_instance_obj('pet_question_rewrite_agent')
        rewrite_agent_res = rewrite_agent.run(**agent_input)
        agent_input['rewrite_question'] = rewrite_agent_res.get_data('rewrite_output')
        # 问题拆分
        planning_agent_res = AgentManager().get_instance_obj('pet_question_planning_agent').run(**agent_input)
        split_questions = planning_agent_res.get_data('planning_output')
        sub_query_list = json.loads(split_questions).get('sub_query_list')

        # 问题检索
        search_tool: Tool = ToolManager().get_instance_obj('pet_insurance_search_context_tool')
        search_res = ''
        for sub_query in sub_query_list:
            search_res += search_tool.run(input=sub_query) + '\n'

        agent_input['search_context'] = search_res

        # llm表达
        process_llm_token(llm, prompt.as_langchain(), self.agent_model.profile, agent_input)
        chain = prompt.as_langchain() | llm.as_langchain_runnable(
            self.agent_model.llm_params()) | StrOutputParser()
        res = self.invoke_chain(chain, agent_input, input_object, **kwargs)
        assemble_memory_output(memory=memory,
                               agent_input=agent_input,
                               content=f"Human: {agent_input.get('input')}, AI: {res}")
        self.add_output_stream(input_object.get_data('output_stream'), res)
        return {**agent_input, 'output': res}
