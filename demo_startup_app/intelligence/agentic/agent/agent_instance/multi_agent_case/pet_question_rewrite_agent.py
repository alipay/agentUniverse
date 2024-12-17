# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/12/12 20:58
# @Author  : jijiawei
# @Email   : jijiawei.jjw@antgroup.com
# @FileName: pet_insurance_rewrite_agent.py
from typing import Optional, Any

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.input_object import InputObject
from agentuniverse.base.config.component_configer.configers.agent_configer import AgentConfiger
from agentuniverse.base.util.common_util import stream_output
from agentuniverse.base.util.logging.logging_util import LOGGER
from agentuniverse.base.util.prompt_util import process_llm_token
from agentuniverse.llm.llm import LLM
from agentuniverse.llm.llm_manager import LLMManager
from agentuniverse.prompt.chat_prompt import ChatPrompt
from agentuniverse.prompt.prompt import Prompt
from agentuniverse.prompt.prompt_manager import PromptManager
from agentuniverse.prompt.prompt_model import AgentPromptModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableSerializable


class PetInsuranceRewriteAgent(Agent):
    llm_name: Optional[str] = ''
    memory_name: Optional[str] = None
    tool_names: Optional[list[str]] = None
    knowledge_names: Optional[list[str]] = None
    prompt_version: Optional[str] = None

    def input_keys(self) -> list[str]:
        return ['input', 'prod_description']

    def output_keys(self) -> list[str]:
        return ['rewrite_output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        agent_input['input'] = input_object.get_data('input')
        agent_input['prod_description'] = input_object.get_data('prod_description')
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        rewrite_output = agent_result['output']
        LOGGER.info(f'智能体 pet_question_planning_agent 执行结果为： {rewrite_output}')
        return {**agent_result, 'rewrite_output': agent_result['output']}

    def execute(self, input_object: InputObject, agent_input: dict, **kwargs) -> dict:
        llm: LLM = self.process_llm(**kwargs)
        prompt: Prompt = self.process_prompt(agent_input, **kwargs)
        return self.customized_execute(input_object, agent_input, llm, prompt, **kwargs)

    def customized_execute(self, input_object: InputObject, agent_input: dict, llm: LLM, prompt: Prompt,
                           **kwargs) -> dict:
        process_llm_token(llm, prompt.as_langchain(), self.agent_model.profile, agent_input)
        chain = prompt.as_langchain() | llm.as_langchain_runnable(
            self.agent_model.llm_params()) | StrOutputParser()
        res = self.invoke_chain(chain, agent_input, input_object, **kwargs)
        return {**agent_input, 'output': res}

    def process_llm(self, **kwargs) -> LLM:
        return LLMManager().get_instance_obj(self.llm_name)

    def process_prompt(self, agent_input: dict, **kwargs) -> ChatPrompt:
        expert_framework = agent_input.pop('expert_framework', '') or ''

        profile: dict = self.agent_model.profile

        profile_instruction = profile.get('instruction')
        profile_instruction = expert_framework + profile_instruction if profile_instruction else profile_instruction

        profile_prompt_model: AgentPromptModel = AgentPromptModel(introduction=profile.get('introduction'),
                                                                  target=profile.get('target'),
                                                                  instruction=profile_instruction)

        # get the prompt by the prompt version
        version_prompt: Prompt = PromptManager().get_instance_obj(self.prompt_version)

        if version_prompt is None and not profile_prompt_model:
            raise Exception("Either the `prompt_version` or `introduction & target & instruction`"
                            " in agent profile configuration should be provided.")
        if version_prompt:
            version_prompt_model: AgentPromptModel = AgentPromptModel(
                introduction=getattr(version_prompt, 'introduction', ''),
                target=getattr(version_prompt, 'target', ''),
                instruction=expert_framework + getattr(version_prompt, 'instruction', ''))
            profile_prompt_model = profile_prompt_model + version_prompt_model

        chat_prompt = ChatPrompt().build_prompt(profile_prompt_model, ['introduction', 'target', 'instruction'])
        image_urls: list = agent_input.pop('image_urls', []) or []
        if image_urls:
            chat_prompt.generate_image_prompt(image_urls)
        return chat_prompt

    def invoke_chain(self, chain: RunnableSerializable[Any, str], agent_input: dict, input_object: InputObject,
                     **kwargs):
        if not input_object.get_data('output_stream'):
            res = chain.invoke(input=agent_input)
            return res
        result = []
        for token in chain.stream(input=agent_input):
            stream_output(input_object.get_data('output_stream', None), {
                'type': 'token',
                'data': {
                    'chunk': token,
                    'agent_info': self.agent_model.info
                }
            })
            result.append(token)
        return "".join(result)

    def initialize_by_component_configer(self, component_configer: AgentConfiger) -> 'RagAgentTemplate':
        super().initialize_by_component_configer(component_configer)
        self.llm_name = self.agent_model.profile.get('llm_model', {}).get('name')
        self.memory_name = self.agent_model.memory.get('name')
        self.tool_names = self.agent_model.action.get('tool', [])
        self.knowledge_names = self.agent_model.action.get('knowledge', [])
        self.prompt_version = self.agent_model.profile.get('prompt_version', 'default_rag_agent.cn')
        return self
