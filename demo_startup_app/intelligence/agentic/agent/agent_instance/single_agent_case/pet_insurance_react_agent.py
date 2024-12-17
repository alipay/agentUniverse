# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/12/12 11:24
# @Author  : jijiawei
# @Email   : jijiawei.jjw@antgroup.com
# @FileName: pet_insurance_react_agent.py
from typing import Sequence, Optional, Union, List

from agentuniverse.agent.memory.memory_manager import MemoryManager
from agentuniverse.base.util.memory_util import generate_messages
from agentuniverse.llm.llm_manager import LLMManager
from agentuniverse.prompt.chat_prompt import ChatPrompt
from agentuniverse.prompt.prompt_manager import PromptManager
from agentuniverse.prompt.prompt_model import AgentPromptModel
from langchain.agents.format_scratchpad import format_log_to_str
from langchain.agents.output_parsers import ReActSingleInputOutputParser
from langchain.agents import AgentExecutor, AgentOutputParser
from langchain.tools import Tool as LangchainTool
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import BasePromptTemplate
from langchain_core.runnables import RunnableConfig, RunnablePassthrough, Runnable
from langchain_core.tools import BaseTool, ToolsRenderer, render_text_description

from agentuniverse.agent.memory.message import Message
from agentuniverse.base.config.component_configer.configers.agent_configer import AgentConfiger
from agentuniverse.base.util.agent_util import assemble_memory_input, assemble_memory_output
from agentuniverse.agent.action.knowledge.knowledge import Knowledge
from agentuniverse.agent.action.knowledge.knowledge_manager import KnowledgeManager
from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.plan.planner.react_planner.stream_callback import StreamOutPutCallbackHandler
from agentuniverse.base.util.prompt_util import process_llm_token
from agentuniverse.llm.llm import LLM
from agentuniverse.prompt.prompt import Prompt


class PetInsuranceReactAgent(Agent):
    agent_names: Optional[list[str]] = None
    stop_sequence: Optional[list[str]] = None
    max_iterations: Optional[int] = None
    llm_name: Optional[str] = ''
    memory_name: Optional[str] = None
    tool_names: Optional[list[str]] = None
    knowledge_names: Optional[list[str]] = None
    prompt_version: Optional[str] = None

    def input_keys(self) -> list[str]:
        return ['input']

    def output_keys(self) -> list[str]:
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        agent_input['input'] = input_object.get_data('input')
        tools_context = self.build_tools_context()
        agent_input['tools'] = tools_context[0]
        agent_input['tool_names'] = tools_context[1]
        agent_input['agent_scratchpad'] = ''
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        return {**agent_result, 'output': agent_result['output']}

    def execute(self, input_object: InputObject, agent_input: dict, **kwargs) -> dict:
        """执行主体"""
        memory: Memory = self.process_memory(agent_input, **kwargs)
        llm: LLM = self.process_llm(**kwargs)
        prompt: Prompt = self.process_prompt(agent_input, **kwargs)
        return self.customized_execute(input_object, agent_input, memory, llm, prompt, **kwargs)

    def process_llm(self, **kwargs) -> LLM:
        return LLMManager().get_instance_obj(self.llm_name)

    def customized_execute(self, input_object: InputObject, agent_input: dict, memory: Memory, llm: LLM, prompt: Prompt,
                           **kwargs) -> dict:
        assemble_memory_input(memory, agent_input)
        process_llm_token(llm, prompt.as_langchain(), self.agent_model.profile, agent_input)
        lc_tools: List[LangchainTool] = self._convert_to_langchain_tool()
        agent = self.create_react_agent(llm.as_langchain(), lc_tools, prompt.as_langchain(),
                                        stop_sequence=self.stop_sequence,
                                        bind_params=self.agent_model.llm_params())
        agent_executor = AgentExecutor(agent=agent, tools=lc_tools,
                                       verbose=True,
                                       handle_parsing_errors=True,
                                       max_iterations=self.max_iterations)
        res = agent_executor.invoke(input=agent_input, memory=memory.as_langchain() if memory else None,
                                    chat_history=agent_input.get(memory.memory_key) if memory else '',
                                    config=self._get_run_config(input_object))
        assemble_memory_output(memory=memory,
                               agent_input=agent_input,
                               content=f"Human: {agent_input.get('input')}, AI: {res.get('output')}")
        return res

    def process_prompt(self, agent_input: dict, **kwargs) -> ChatPrompt:
        """处理提示词"""
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

    def process_memory(self, agent_input: dict, **kwargs) -> Memory | None:
        """处理记忆"""
        memory: Memory = MemoryManager().get_instance_obj(component_instance_name=self.memory_name)
        if memory is None:
            return None

        chat_history: list = agent_input.get('chat_history')
        # generate a list of temporary messages from the given chat history and add them to the memory instance.
        temporary_messages: list[Message] = generate_messages(chat_history)
        if temporary_messages:
            memory.add(temporary_messages, **agent_input)

        params: dict = dict()
        params['agent_llm_name'] = self.llm_name
        return memory.set_by_agent_model(**params)

    def create_react_agent(
            self,
            llm: BaseLanguageModel,
            tools: Sequence[BaseTool],
            prompt: BasePromptTemplate,
            output_parser: Optional[AgentOutputParser] = None,
            tools_renderer: ToolsRenderer = render_text_description,
            *,
            stop_sequence: Union[bool, List[str]] = True,
            bind_params: Optional[dict],
    ) -> Runnable:
        missing_vars = {"tools", "tool_names", "agent_scratchpad"}.difference(
            prompt.input_variables + list(prompt.partial_variables)
        )
        if missing_vars:
            raise ValueError(f"Prompt missing required variables: {missing_vars}")

        prompt = prompt.partial(
            tools=tools_renderer(list(tools)),
            tool_names=", ".join([t.name for t in tools]),
        )
        if stop_sequence:
            stop = ["\nObservation"] if stop_sequence is True else stop_sequence
            llm_with_stop = llm.bind(stop=stop, **(bind_params or {}))
        else:
            llm_with_stop = llm.bind(**(bind_params or {}))
        output_parser = output_parser or ReActSingleInputOutputParser()
        agent = (
                RunnablePassthrough.assign(
                    agent_scratchpad=lambda x: format_log_to_str(x["intermediate_steps"]),
                )
                | prompt
                | llm_with_stop
                | output_parser
        )
        return agent

    def build_tools_context(self) -> tuple[str, str]:
        lc_tools: [LangchainTool] = self._convert_to_langchain_tool()
        tools_context = ''
        if not lc_tools:
            return '', ''
        tool_names = []
        for lc_tool in lc_tools:
            tools_context += f"tool name: {lc_tool.name}, tool description: {lc_tool.description}\n"
        return tools_context, "|".join(tool_names)

    def _convert_to_langchain_tool(self) -> list[LangchainTool]:
        lc_tools = []
        if self.tool_names:
            for tool_name in self.tool_names:
                tool: Tool = ToolManager().get_instance_obj(tool_name)
                lc_tools.append(tool.as_langchain())
        if self.knowledge_names:
            for knowledge_name in self.knowledge_names:
                knowledge: Knowledge = KnowledgeManager().get_instance_obj(knowledge_name)
                lc_tools.append(knowledge.as_langchain_tool())
        if self.agent_names:
            for agent_name in self.agent_names:
                agent: Agent = AgentManager().get_instance_obj(agent_name)
                lc_tools.append(agent.as_langchain_tool())
        return lc_tools

    def _get_run_config(self, input_object: InputObject) -> RunnableConfig:
        config = RunnableConfig()
        callbacks = []
        output_stream = input_object.get_data('output_stream')
        callbacks.append(StreamOutPutCallbackHandler(output_stream, agent_info=self.agent_model.info))
        config.setdefault("callbacks", callbacks)
        return config

    def initialize_by_component_configer(self, component_configer: AgentConfiger) -> 'ReActAgentTemplate':
        super().initialize_by_component_configer(component_configer)
        self.llm_name = self.agent_model.profile.get('llm_model', {}).get('name')
        self.memory_name = self.agent_model.memory.get('name')
        self.tool_names = self.agent_model.action.get('tool', [])
        self.knowledge_names = self.agent_model.action.get('knowledge', [])
        self.prompt_version = self.agent_model.profile.get('prompt_version', 'default_react_agent.cn')
        self.stop_sequence = self.agent_model.profile.get('stop_sequence')
        self.max_iterations = self.agent_model.profile.get('max_iterations', 5)
        self.agent_names = self.agent_model.action.get('agent', [])
        return self
