# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/17 14:26
# @Author  : weizjajj
# @Email   : weizhongjie.wzj@antgroup.com
# @FileName: rag_agent_case_template.py

import datetime
from threading import Thread

from langchain_core.output_parsers import StrOutputParser

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.memory.message import Message
from agentuniverse.agent.template.rag_agent_template import RagAgentTemplate
from agentuniverse.base.context.framework_context_manager import FrameworkContextManager
from agentuniverse.base.util.agent_util import assemble_memory_input, assemble_memory_output
from agentuniverse.base.util.prompt_util import process_llm_token
from agentuniverse.llm.llm import LLM
from agentuniverse.prompt.prompt import Prompt


class RagAgentCaseTemplate(RagAgentTemplate):

    def summarize_memory(self, agent_input: dict, memory: Memory):
        session_id = agent_input.get('session_id')
        if not session_id:
            session_id = FrameworkContextManager().get_context('session_id')
            agent_input['session_id'] = session_id

        def do_summarize():
            summarized_memory = memory.summarize_memory(
                **self.get_memory_params(agent_input)
            )
            message = Message(content=summarized_memory, source=self.agent_model.info.get('name'), type='summarize',
                              metadata={
                                  'timestamp': datetime.datetime.now(),
                                  'gmt_created': datetime.datetime.now().timestamp(),
                                  "session_id": session_id
                              })
            memory.add([message], session_id=session_id)

        Thread(target=do_summarize).start()

    def load_summarize_memory(self, memory: Memory, session_id) -> str:
        if session_id is None:
            session_id = FrameworkContextManager().get_context('session_id')
        result = memory.get(
            session_id=session_id,
            agent_id=self.agent_model.info.get('name'),
            memory_type='summarize'
        )
        if len(result) == 0:
            return "no summarize memory"
        return result[-1].content

    def customized_execute(self, input_object: InputObject, agent_input: dict, memory: Memory, llm: LLM, prompt: Prompt,
                           **kwargs) -> dict:
        tool_res: str = self.invoke_tools(input_object)
        knowledge_res: str = self.invoke_knowledge(agent_input.get('input'), input_object)
        agent_input['background'] = (agent_input['background']
                                     + f"{tool_res} \n\n {knowledge_res}")
        assemble_memory_input(memory, agent_input, self.get_memory_params(agent_input))
        if not agent_input['chat_history']:
            agent_input['chat_history'] = "No Chat History"
        summarize_memory = self.load_summarize_memory(memory, agent_input.get('session_id'))
        agent_input['background'] = (agent_input['background']
                                     + f"\nsummarize_memory:\n {summarize_memory}")
        process_llm_token(llm, prompt.as_langchain(), self.agent_model.profile, agent_input)
        chain = prompt.as_langchain() | llm.as_langchain_runnable(
            self.agent_model.llm_params()) | StrOutputParser()
        res = self.invoke_chain(chain, agent_input, input_object, **kwargs)
        self.add_output_stream(input_object.get_data('output_stream'), res)
        self.summarize_memory(agent_input, memory)
        return {**agent_input, 'output': res}
