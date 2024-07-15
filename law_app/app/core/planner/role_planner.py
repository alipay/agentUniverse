#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time   : 2024/7/10 10:10
# @Author : fluchw
# @Email  : zerozed00@qq.com
# @File   ：draft_contract_planner.py
import asyncio

from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory

from agentuniverse.agent.agent_model import AgentModel
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.chat_memory import ChatMemory
from agentuniverse.agent.plan.planner.planner import Planner
from agentuniverse.base.util.logging.logging_util import LOGGER
from agentuniverse.base.util.memory_util import generate_memories
from agentuniverse.base.util.prompt_util import process_llm_token
from agentuniverse.llm.llm import LLM
from agentuniverse.prompt.chat_prompt import ChatPrompt
from agentuniverse.prompt.prompt import Prompt
from agentuniverse.prompt.prompt_manager import PromptManager
from agentuniverse.prompt.prompt_model import AgentPromptModel
from loguru import logger


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
        # 处理内存模块
        memory: ChatMemory = self.handle_memory(agent_model, planner_input)

        LOGGER.debug("↓↓↓↓↓↓↓")
        # 运行所有工具和知识模块
        self.run_all_actions(agent_model, planner_input, input_object)
        LOGGER.debug("↑↑↑↑↑↑↑")
        # 处理语言模型
        llm: LLM = self.handle_llm(agent_model)

        # 处理提示模块
        prompt: ChatPrompt = self.handle_prompt(agent_model, planner_input)
        process_llm_token(llm, prompt.as_langchain(), agent_model.profile, planner_input)

        # 首先检查memory是否存在，如果存在，则使用memory提供的聊天历史管理器
        # chat_history = memory.as_langchain().chat_memory if memory else InMemoryChatMessageHistory()
        try:
            if memory is not None:
                LOGGER.debug("memory已存在")

                # memory对象必须提供as_langchain()方法，该方法返回一个LangChain兼容的接口
                # .chat_memory是从这个接口获取的聊天历史管理器
                chat_history = memory.as_langchain().chat_memory
            else:
                # 如果memory不存在，则创建一个新的InMemoryChatMessageHistory实例
                # 这将用于在内存中存储聊天历史
                LOGGER.debug("memory不存在")

                chat_history = InMemoryChatMessageHistory()
        except Exception as e:
            logger.exception(f"未预料的错误：{e}")

        def get_chat_history(session_id):
            return chat_history

        # 生成包含历史记录的可运行链
        chain_with_history = RunnableWithMessageHistory(
            prompt.as_langchain() | llm.as_langchain(),
            get_chat_history,
            history_messages_key="chat_history",
            input_messages_key=self.input_key,
        ) | StrOutputParser()

        # 异步调用链并获取结果
        res = asyncio.run(
            chain_with_history.ainvoke(input=planner_input, config={"configurable": {"session_id": "unused"}}))

        LOGGER.debug(f"chat_history {chat_history}")
        # 返回结果，包括计划器输入、输出和生成的聊天历史
        return {**planner_input, self.output_key: res, 'chat_history': generate_memories(chat_history)}

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
            raise Exception(f"在 Agent 配置文件中应该提供 `prompt_version` {prompt_version} 或 `introduction & target & instruction`。")

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
