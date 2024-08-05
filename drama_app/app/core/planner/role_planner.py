#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time   : 2024/7/10 10:10
# @Author : fluchw
# @Email  : zerozed00@qq.com
# @File   ：draft_contract_planner.py
from typing import List, Any

from agentuniverse.agent.agent_model import AgentModel
from agentuniverse.agent.input_object import InputObject
# from agentuniverse.agent.memory.chat_memory import RoleChatMemory
from agentuniverse.agent.memory.memory_manager import MemoryManager
# from agentuniverse.agent.memory.message import ChatMessage
from agentuniverse.agent.plan.planner.planner import Planner
from agentuniverse.base.util.logging.logging_util import LOGGER
from agentuniverse.base.util.prompt_util import process_llm_token
from agentuniverse.llm.llm import LLM
from agentuniverse.llm.llm_manager import LLMManager
from agentuniverse.prompt.chat_prompt import ChatPrompt
from agentuniverse.prompt.prompt import Prompt
from agentuniverse.prompt.prompt_manager import PromptManager
from agentuniverse.prompt.prompt_model import AgentPromptModel
from drama_app.app.core.memory.role.role_chat_memory import RoleChatMemory
from langchain.memory import ChatMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import ChatMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableSerializable
from langchain_core.runnables.history import RunnableWithMessageHistory


# from drama_app.app.core.memory.role_message import ChatMessage


class role_planner(Planner):
    """Rag 计划器类。"""

    def invoke(self, agent_model: AgentModel, planner_input: dict,
               input_object: InputObject) -> dict:
        """调用计划器。

        参数:
            agent_model (AgentModel): Agent 模型对象。
            planner_input (dict): 计划器输入对象。
            input_object (InputObject): 用户传递的输入参数。
        返回:
            dict: 计划器结果。
        """
        # 处理记忆模块
        memory: RoleChatMemory = self.handle_memory(agent_model, planner_input)

        LOGGER.debug("↓↓↓↓↓↓↓")
        # 运行所有工具和知识模块
        self.run_all_actions(agent_model, planner_input, input_object)
        LOGGER.debug("↑↑↑↑↑↑↑")
        # 处理语言模型
        llm: LLM = self.handle_llm(agent_model)

        LOGGER.debug(f"planner_input {planner_input}")
        # 处理提示模块
        prompt: ChatPrompt = self.handle_prompt(agent_model, planner_input)
        process_llm_token(llm, prompt.as_langchain(), agent_model.profile, planner_input)
        LOGGER.debug(f"prompt {prompt}")

        # 首先检查memory是否存在，如果存在，则使用memory提供的聊天历史管理器
        if memory:
            LOGGER.debug("使用来自 memory 的聊天历史记录。")
            chat_history = memory.as_langchain().chat_memory
            LOGGER.debug(f"chat_history {chat_history}")

        else:
            LOGGER.debug("创建新的内存聊天历史记录。")
            chat_history = InMemoryChatMessageHistory()
            LOGGER.debug(f"chat_history {chat_history}")

        # chat_history: BaseChatMessageHistory = add_message
        LOGGER.debug(f"chat_history {chat_history}")

        chain_with_history = RunnableWithMessageHistory(
            prompt.as_langchain() | llm.as_langchain(),
            lambda session_id: chat_history,
            history_messages_key="chat_history",
            # input_messages_key=self.input_key,
            # verbose=True,
        ) | StrOutputParser()
        LOGGER.debug(f"chat_history {chat_history}")

        LOGGER.debug(f"chain_with_history {chain_with_history}")
        res = self.invoke_chain(agent_model, chain_with_history, planner_input, chat_history, input_object)

        LOGGER.debug(f"res {res}")
        LOGGER.debug(f"chat_history {chat_history}")
        # r = {**planner_input, self.output_key: res, 'chat_history': chat_history}
        r = {**planner_input, self.output_key: res, 'chat_history': self.generate_memories(chat_history)}
        LOGGER.debug(f"r {r}")

        return r

        # LOGGER.debug(f"chat_history1 --> {self.generate_memories(chat_history)}")
        # 返回结果，包括计划器输入、输出和生成的聊天历史
        # redata = {**planner_input, self.output_key: res, 'chat_history': self.generate_memories(chat_history)}
        # LOGGER.debug(f"redata {redata}")
        # return redata

    def invoke_chain(self,
                     agent_model: AgentModel,
                     chain: RunnableSerializable[Any, str],
                     planner_input: dict,
                     chat_history,
                     input_object: InputObject):

        LOGGER.info(f"role invoke_chain\n{chat_history}")
        LOGGER.debug(f"planner_input\n{planner_input}")
        del planner_input['input']
        if not input_object.get_data('output_stream'):
            res = chain.invoke(input=planner_input, config={"configurable": {"session_id": "test_session_id"}})
            LOGGER.debug(f"返回res {res}")
            LOGGER.info(f"role invoke_chain\n{chat_history}")

            return res
        result = []
        for token in chain.stream(input=planner_input, config={"configurable": {"session_id": "unused"}}):
            self.stream_output(input_object, {
                'type': 'token',
                'data': {
                    'chunk': token,
                    'agent_info': agent_model.info
                }
            })
            result.append(token)
            LOGGER.debug(f"返回resule {result}")
        return "".join(result)

    def generate_messages(self, memories: list) -> List[ChatMessage]:
        messages = []
        for memory in memories:
            LOGGER.debug(memory)
            message: ChatMessage = ChatMessage(role=memory.get('role'), type=memory.get('type'),
                                               content=memory.get('content'))
            messages.append(message)
        return messages

    def generate_memories(self, chat_messages: ChatMessageHistory) -> list:
        memories = []
        if chat_messages.messages:
            LOGGER.debug(f"chat_messages.messages {chat_messages.messages}")
            for message in chat_messages.messages:
                LOGGER.debug(f'generate_memories -> {message}')
                LOGGER.debug(f'message.type -> {message.type}')
                memory_dict = {"role": message.role, "content": message.content, "type": message.type}
                memories.append(memory_dict)
        return memories

    def handle_memory(self, agent_model: AgentModel, planner_input: dict) -> RoleChatMemory | None:
        """Memory module processing.

        Args:
            agent_model (AgentModel): Agent model object.
            planner_input (dict): Planner input object.
        Returns:
             Memory: The memory.
        """
        chat_history: list = planner_input.get('chat_history')
        LOGGER.debug(f"handle_memory chat_history {type(chat_history)}")
        memory_name = agent_model.memory.get('name')
        llm_model = agent_model.memory.get('llm_model') or dict()
        llm_name = llm_model.get('name') or agent_model.profile.get('llm_model').get('name')

        messages: list[ChatMessage] = self.generate_messages(chat_history)
        LOGGER.debug(f'generate_messages(chat_history) -> {messages}')
        llm: LLM = LLMManager().get_instance_obj(llm_name)
        params: dict = dict()
        params['messages'] = messages
        params['llm'] = llm
        params['input_key'] = self.input_key
        params['output_key'] = self.output_key
        LOGGER.debug(f"params {params}")
        memory: RoleChatMemory = MemoryManager().get_instance_obj(component_instance_name=memory_name)
        if memory is None:
            return None

        rem = memory.set_by_agent_model(**params)
        LOGGER.debug(f"rem {rem}")
        return rem

    def handle_prompt(self, agent_model: AgentModel, planner_input: dict) -> ChatPrompt:
        """提示模块处理。

        参数:
            agent_model (AgentModel): Agent 模型对象。
            planner_input (dict): 计划器输入对象。
        返回:
            ChatPrompt: 聊天提示实例。
        """
        profile: dict = agent_model.profile

        # 构建提示模型
        profile_prompt_model: AgentPromptModel = AgentPromptModel(
            introduction=profile.get('introduction'),
            target=profile.get('target'),
            instruction=profile.get('instruction')
        )

        # 获取提示版本
        prompt_version: str = profile.get('prompt_version')
        version_prompt: Prompt = PromptManager().get_instance_obj(prompt_version)

        # 检查提示版本和提示模型是否存在
        if version_prompt is None and not profile_prompt_model:
            raise Exception(
                f"在 Agent 配置文件中应该提供 `prompt_version` {prompt_version} 或 `introduction & target & instruction`。")

        # 如果存在提示版本，合并提示模型
        if version_prompt:
            version_prompt_model: AgentPromptModel = AgentPromptModel(
                introduction=getattr(version_prompt, 'introduction', ''),
                target=getattr(version_prompt, 'target', ''),
                instruction=getattr(version_prompt, 'instruction', '')
            )
            profile_prompt_model = profile_prompt_model + version_prompt_model

        # 构建聊天提示
        chat_prompt = ChatPrompt().build_prompt(profile_prompt_model, self.prompt_assemble_order)

        # 处理图像 URL
        image_urls: list = planner_input.pop('image_urls', []) or []
        if image_urls:
            chat_prompt.generate_image_prompt(image_urls)

        return chat_prompt
