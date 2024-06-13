# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/5/31 21:22
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: react_planner.py

from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool as LangchainTool
from langchain_core.runnables import RunnableConfig

from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.agent.agent_model import AgentModel
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.chat_memory import ChatMemory
from agentuniverse.agent.plan.planner.planner import Planner
from agentuniverse.agent.plan.planner.react_planner.stream_callback import StreamOutPutCallbackHandler
from agentuniverse.base.util.prompt_util import process_llm_token
from agentuniverse.llm.llm import LLM
from agentuniverse.prompt.chat_prompt import ChatPrompt
from agentuniverse.prompt.prompt import Prompt
from agentuniverse.prompt.prompt_manager import PromptManager
from agentuniverse.prompt.prompt_model import AgentPromptModel


class ReActPlanner(Planner):
    """ReAct planner class."""

    tools: list[LangchainTool] = None

    def invoke(self, agent_model: AgentModel, planner_input: dict,
               input_object: InputObject) -> dict:
        """Invoke the planner.

        Args:
            agent_model (AgentModel): Agent model object.
            planner_input (dict): Planner input object.
            input_object (InputObject): The input parameters passed by the user.
        Returns:
            dict: The planner result.
        """

        memory: ChatMemory = self.handle_memory(agent_model, planner_input)

        llm: LLM = self.handle_llm(agent_model)

        tools = self.acquire_tools(agent_model.action)

        prompt: Prompt = self.handle_prompt(agent_model, planner_input)
        process_llm_token(llm, prompt.as_langchain(), agent_model.profile, planner_input)
        chat_history = memory.as_langchain().chat_memory if memory else InMemoryChatMessageHistory()

        agent = create_react_agent(llm.as_langchain(), tools, prompt.as_langchain())
        agent_executor = AgentExecutor(agent=agent, tools=tools,
                                       verbose=True,
                                       handle_parsing_errors=True,
                                       max_iterations=agent_model.plan.get('planner').get("max_iterations", 15))

        return agent_executor.invoke(input=planner_input, memory=memory.as_langchain() if memory else None,
                                     chat_history=chat_history, config=self.get_run_config(input_object))

    @staticmethod
    def get_run_config(input_object: InputObject) -> RunnableConfig:
        config = RunnableConfig()
        callbacks = []
        output_stream = input_object.get_data('output_stream')
        callbacks.append(StreamOutPutCallbackHandler(output_stream))
        config.setdefault("callbacks", callbacks)
        return config

    @staticmethod
    def acquire_tools(action) -> list[LangchainTool]:
        tool_names: list = action.get('tool') or list()
        lc_tools: list[LangchainTool] = list()
        for tool_name in tool_names:
            tool: Tool = ToolManager().get_instance_obj(tool_name)
            lc_tools.append(tool.as_langchain())
        return lc_tools

    def handle_prompt(self, agent_model: AgentModel, planner_input: dict) -> Prompt:
        """Prompt module processing.

        Args:
            agent_model (AgentModel): Agent model object.
            planner_input (dict): Planner input object.
        Returns:
            ChatPrompt: The chat prompt instance.
        """
        lc_tools_str: str = ''
        tools = self.acquire_tools(agent_model.action)
        for lc_tool in self.acquire_tools(agent_model.action):
            lc_tools_str += "tool name:" + lc_tool.name + " " + "tool description:" + lc_tool.description + '\n'
        lc_tool_names = "|".join([lc_tool.name for lc_tool in tools])
        planner_input['tool_names'] = lc_tool_names
        planner_input['tools'] = lc_tools_str
        planner_input['agent_scratchpad'] = ''

        profile: dict = agent_model.profile

        profile_prompt_model: AgentPromptModel = AgentPromptModel(introduction=profile.get('introduction'),
                                                                  target=profile.get('target'),
                                                                  instruction=profile.get('instruction'))

        # get the prompt by the prompt version
        prompt_version: str = profile.get('prompt_version')
        version_prompt: Prompt = PromptManager().get_instance_obj(prompt_version)

        if version_prompt is None and not profile_prompt_model:
            raise Exception("Either the `prompt_version` or `introduction & target & instruction`"
                            " in agent profile configuration should be provided.")
        if version_prompt:
            version_prompt_model: AgentPromptModel = AgentPromptModel(
                introduction=getattr(version_prompt, 'introduction', ''),
                target=getattr(version_prompt, 'target', ''),
                instruction=getattr(version_prompt, 'instruction', ''))
            profile_prompt_model = profile_prompt_model + version_prompt_model

        prompt = Prompt().build_prompt(profile_prompt_model, self.prompt_assemble_order)
        return prompt
