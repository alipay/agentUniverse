# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/25 21:11
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: agent_service.py
from datetime import datetime
import json
import time
from typing import List, Tuple, Iterator

from agentuniverse.agent.action.knowledge.knowledge import Knowledge
from agentuniverse.agent.action.knowledge.knowledge_manager import KnowledgeManager
from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.agent_model import AgentModel
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent_serve.web.request_task import RequestTask
from agentuniverse.agent_serve.web.web_util import agent_run_queue
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.util.monitor.monitor import Monitor
from agentuniverse.llm.llm import LLM
from agentuniverse.llm.llm_manager import LLMManager
from agentuniverse.prompt.prompt import Prompt
from agentuniverse.prompt.prompt_manager import PromptManager
from agentuniverse.prompt.prompt_model import AgentPromptModel
from agentuniverse_product.base.product import Product
from agentuniverse_product.base.product_manager import ProductManager
from agentuniverse_product.base.util.yaml_util import update_nested_yaml_value
from agentuniverse_product.service.message_service.message_service import MessageService
from agentuniverse_product.service.model.agent_dto import AgentDTO
from agentuniverse_product.service.model.knowledge_dto import KnowledgeDTO
from agentuniverse_product.service.model.llm_dto import LlmDTO
from agentuniverse_product.service.model.message_dto import MessageDTO
from agentuniverse_product.service.model.planner_dto import PlannerDTO
from agentuniverse_product.service.model.prompt_dto import PromptDTO
from agentuniverse_product.service.model.session_dto import SessionDTO
from agentuniverse_product.service.model.tool_dto import ToolDTO
from agentuniverse_product.service.session_service.session_service import SessionService


class AgentService:
    """Agent Service for aU-product."""

    @staticmethod
    def get_agent_list() -> List[AgentDTO]:
        """Get all agents.

        Returns:
            List[AgentDTO]: List of AgentDTOs.
        """
        res = []
        product_list: List[Product] = ProductManager().get_instance_obj_list()
        if len(product_list) < 1:
            return res
        for product in product_list:
            if product.type == ComponentEnum.AGENT.value:
                agent_dto = AgentDTO(nickname=product.nickname, avatar=product.avatar, id=product.id,
                                     opening_speech=product.opening_speech)
                agent = product.instance
                agent_model: AgentModel = agent.agent_model
                agent_dto.description = agent_model.info.get('description', '')
                res.append(agent_dto)
        return res

    @staticmethod
    def get_agent_detail(id: str) -> AgentDTO | None:
        """Get agent detail by agent id.

        Returns:
            AgentDTO | None: AgentDTO or None.
        """
        product: Product = ProductManager().get_instance_obj(id)
        agent: Agent = AgentManager().get_instance_obj(id)
        if agent is None:
            raise ValueError("The agent instance corresponding to the agent id cannot be found.")
        agent_dto = AgentDTO(id=id,
                             nickname=product.nickname if product else '',
                             avatar=product.avatar if product else '',
                             opening_speech=product.opening_speech if product else '')
        # assemble agent dto
        return AgentService().assemble_agent_dto(agent, agent_dto)

    @staticmethod
    def update_agent(agent_dto: AgentDTO) -> None:
        """Update agent detail."""
        if agent_dto.id is None:
            raise ValueError("Agent id cannot be None.")
        product: Product = ProductManager().get_instance_obj(agent_dto.id)
        agent: Agent = AgentManager().get_instance_obj(agent_dto.id)
        if agent is None:
            raise ValueError("The agent instance corresponding to the agent id cannot be found.")
        # update agent product yaml configuration file
        if product:
            AgentService().update_agent_product_config(product, agent_dto, product.component_config_path)
        # update agent yaml configuration file
        AgentService().update_agent_config(agent, agent_dto, agent.component_config_path)

    @staticmethod
    def chat(agent_id: str, session_id: str, input: str) -> dict:
        """Chat with agent and get response.

        Args:
            agent_id (str): Agent id.
            session_id (str): Session id.
            input (str): Query string.
        Returns:
            dict: Response.
        """
        if agent_id is None or session_id is None:
            raise ValueError("Agent id or session id cannot be None.")
        agent: Agent = AgentManager().get_instance_obj(agent_id)
        if agent is None:
            raise ValueError("The agent instance corresponding to the agent id cannot be found.")

        # init the invocation chain and token usage of the monitor module
        Monitor.init_invocation_chain()
        Monitor.init_token_usage()

        # invoke agent
        start_time = time.time()
        output_object: OutputObject = agent.run(input=input,
                                                chat_history=AgentService().get_agent_chat_history(session_id))
        end_time = time.time()
        # calculate response time
        response_time = round((end_time - start_time) * 1000, 2)
        output = output_object.get_data('output')

        # get and clear invocation chain and token usage.
        invocation_chain = Monitor.get_invocation_chain()
        token_usage = Monitor.get_token_usage()
        Monitor.clear_invocation_chain()
        Monitor.clear_token_usage()

        # add agent chat history
        session_id, message_id = AgentService().add_agent_chat_history(agent_id, session_id, input, output,
                                                                       datetime.fromtimestamp(end_time))

        return {'response_time': response_time, 'message_id': message_id, 'session_id': session_id, 'output': output,
                'start_time': datetime.fromtimestamp(start_time).strftime("%Y-%m-%d %H:%M:%S"),
                'end_time': datetime.fromtimestamp(end_time).strftime("%Y-%m-%d %H:%M:%S"),
                'invocation_chain': invocation_chain, 'token_usage': token_usage}

    @staticmethod
    def stream_chat(agent_id: str, session_id: str, input: str) -> Iterator:
        """Stream chat with agent and get response.

        Args:
            agent_id (str): Agent id.
            session_id (str): Session id.
            input (str): Query string.
        Returns:
            Iterator: Response.
        """
        if agent_id is None or session_id is None:
            raise ValueError("Agent id or session id cannot be None.")
        agent: Agent = AgentManager().get_instance_obj(agent_id)
        if agent is None:
            raise ValueError("The agent instance corresponding to the agent id cannot be found.")

        # init the invocation chain and token usage of the monitor module
        Monitor.init_invocation_chain()
        Monitor.init_token_usage()

        # invoke agent
        start_time = time.time()
        task = RequestTask(agent_run_queue, False,
                           **{'input': input, 'chat_history': AgentService().get_agent_chat_history(session_id),
                              'agent_id': agent_id})
        # get output stream
        output_iterator = task.stream_run()

        final_result: dict = dict()
        error_result: dict = dict()
        # generate iterator
        for chunk in output_iterator:
            chunk = chunk.replace("data:", "", 1)
            chunk_dict = json.loads(chunk)
            if "process" in chunk_dict:
                data = chunk_dict['process'].get('data')
                cur_agent_id = data.get('agent_info', {}).get('name', '')
                if data and "chunk" in data:
                    yield {'output': data['chunk'], 'type': 'token', 'agent_id': cur_agent_id}
                elif data and "output" in data:
                    yield {'output': data['output'], 'type': 'intermediate_steps', 'agent_id': cur_agent_id}
            elif "result" in chunk_dict:
                final_result = chunk_dict['result']
            elif "error" in chunk_dict:
                error_result = chunk_dict['error']

        end_time = time.time()
        # calculate response time
        response_time = round((end_time - start_time) * 1000, 2)

        if len(final_result) > 0:
            output = final_result.get('output')

            # add agent chat history
            session_id, message_id = AgentService().add_agent_chat_history(agent_id, session_id, input, output,
                                                                           datetime.fromtimestamp(end_time))

            # get and clear invocation chain and invocation chain.
            invocation_chain = Monitor.get_invocation_chain()
            token_usage = Monitor.get_token_usage()
            Monitor.clear_invocation_chain()
            Monitor.clear_token_usage()

            # return final yield
            yield {'response_time': response_time, 'message_id': message_id, 'session_id': session_id, 'output': output,
                   'start_time': datetime.fromtimestamp(start_time).strftime("%Y-%m-%d %H:%M:%S"),
                   'end_time': datetime.fromtimestamp(end_time).strftime("%Y-%m-%d %H:%M:%S"),
                   'invocation_chain': invocation_chain, 'token_usage': token_usage, 'type': 'final_result'}
        else:
            yield {'error': error_result, 'type': 'error'}

    @staticmethod
    def get_planner_dto(agent_model: AgentModel) -> PlannerDTO | None:
        """Get planner dto."""
        planner = agent_model.plan.get('planner', {})
        planner_name = planner.get('name')
        if planner_name is None:
            return None
        product: Product = ProductManager().get_instance_obj(planner_name)

        members = None
        if getattr(product, 'member_keys', None):
            # assemble multi-agent members
            members = AgentService().assemble_planner_members(planner, product.member_keys)
        return PlannerDTO(nickname=product.nickname if product else '', id=planner_name, members=members)

    @staticmethod
    def get_knowledge_dto_list(agent_model: AgentModel) -> List[KnowledgeDTO]:
        """Get knowledge dto list."""
        knowledge_name_list = agent_model.action.get('knowledge', [])
        res = []
        if len(knowledge_name_list) < 1:
            return res
        for knowledge_name in knowledge_name_list:
            product: Product = ProductManager().get_instance_obj(knowledge_name)
            knowledge: Knowledge = KnowledgeManager().get_instance_obj(knowledge_name)
            if knowledge is None:
                continue
            knowledge_dto = KnowledgeDTO(nickname=product.nickname if product else '', id=knowledge_name)
            knowledge_dto.description = knowledge.description
            res.append(knowledge_dto)
        return res

    @staticmethod
    def get_tool_dto_list(agent_model: AgentModel) -> List[ToolDTO]:
        """Get tool dto list."""
        tool_name_list = agent_model.action.get('tool', [])
        res = []
        if len(tool_name_list) < 1:
            return res
        for tool_name in tool_name_list:
            product: Product = ProductManager().get_instance_obj(tool_name)
            tool: Tool = ToolManager().get_instance_obj(tool_name)
            tool_dto = ToolDTO(nickname=product.nickname if product is not None else '',
                               avatar=product.avatar if product is not None else '',
                               id=tool.name)
            tool_dto.description = tool.description
            res.append(tool_dto)
        return res

    @staticmethod
    def get_prompt_dto(agent_model: AgentModel) -> PromptDTO | None:
        """Get prompt dto."""
        profile_prompt_model: AgentPromptModel = AgentPromptModel(
            introduction=agent_model.profile.get('introduction'),
            target=agent_model.profile.get('target'),
            instruction=agent_model.profile.get('instruction'))

        prompt_version = agent_model.profile.get('prompt_version')
        version_prompt: Prompt = PromptManager().get_instance_obj(prompt_version)

        if version_prompt:
            version_prompt_model: AgentPromptModel = AgentPromptModel(
                introduction=getattr(version_prompt, 'introduction', ''),
                target=getattr(version_prompt, 'target', ''),
                instruction=getattr(version_prompt, 'instruction', ''))
            profile_prompt_model = profile_prompt_model + version_prompt_model
        if not profile_prompt_model:
            return None
        return PromptDTO(introduction=profile_prompt_model.introduction, target=profile_prompt_model.target,
                         instruction=profile_prompt_model.instruction)

    @staticmethod
    def get_llm_dto(agent_model: AgentModel) -> LlmDTO | None:
        """Get llm dto from agent."""
        llm_model = agent_model.profile.get('llm_model', {})
        llm_id = llm_model.get('name')
        llm: LLM = LLMManager().get_instance_obj(llm_id)
        product: Product = ProductManager().get_instance_obj(llm_id)
        if llm is None:
            return None
        llm_model_name = llm_model.get('model_name') if llm_model.get('model_name') else llm.model_name
        llm_temperature = llm_model.get('temperature') if llm_model.get('temperature') else llm.temperature
        return LlmDTO(id=llm_id, nickname=product.nickname if product else '', temperature=llm_temperature,
                      model_name=[llm_model_name])

    @staticmethod
    def update_agent_product_config(agent_product: Product, agent_dto: AgentDTO, product_config_path: str) -> None:
        """Update agent product instance and configuration yaml file."""
        if agent_dto is None or agent_dto.opening_speech is None:
            return
        agent_product.opening_speech = agent_dto.opening_speech
        update_nested_yaml_value(product_config_path, {'opening_speech': agent_dto.opening_speech})

    @staticmethod
    def update_agent_config(agent: Agent, agent_dto: AgentDTO, agent_config_path: str) -> None:
        """Update agent instance and configuration yaml file."""
        agent_updates = {}
        if agent_dto.description is not None and agent_dto.description != "":
            agent_updates['info.description'] = agent_dto.description
            agent.agent_model.info['description'] = agent_dto.description
        if agent_dto.prompt is not None:
            prompt_dto = agent_dto.prompt
            if prompt_dto.target is not None:
                agent_updates['profile.target'] = agent_dto.prompt.target
                agent.agent_model.profile['target'] = agent_dto.prompt.target
            if prompt_dto.introduction is not None:
                agent_updates['profile.introduction'] = agent_dto.prompt.introduction
                agent.agent_model.profile['introduction'] = agent_dto.prompt.introduction
            if prompt_dto.instruction is not None:
                agent_updates['profile.instruction'] = agent_dto.prompt.instruction
                agent.agent_model.profile['instruction'] = agent_dto.prompt.instruction
        if agent_dto.llm is not None:
            llm_dto = agent_dto.llm
            if llm_dto.id is not None:
                agent_updates['profile.llm_model.name'] = agent_dto.llm.id
                agent.agent_model.profile.get('llm_model')['name'] = agent_dto.llm.id
            if llm_dto.temperature is not None:
                agent_updates['profile.llm_model.temperature'] = agent_dto.llm.temperature
                agent.agent_model.profile.get('llm_model')['temperature'] = agent_dto.llm.temperature
            if llm_dto.model_name is not None:
                agent_updates['profile.llm_model.model_name'] = agent_dto.llm.model_name[0]
                agent.agent_model.profile.get('llm_model')['model_name'] = agent_dto.llm.model_name[0]
        if agent_dto.tool is not None:
            tool_dto_list: List[ToolDTO] = agent_dto.tool
            tool_name_list = [tool_dto.id for tool_dto in tool_dto_list]
            agent_updates['action.tool'] = tool_name_list
            agent.agent_model.action['tool'] = tool_name_list
        if agent_dto.knowledge is not None:
            knowledge_dto_list: List[KnowledgeDTO] = agent_dto.knowledge
            knowledge_name_list = [knowledge_dto.id for knowledge_dto in knowledge_dto_list]
            agent_updates['action.knowledge'] = knowledge_name_list
            agent.agent_model.action['knowledge'] = knowledge_name_list
        if agent_updates:
            update_nested_yaml_value(agent_config_path, agent_updates)

    @staticmethod
    def get_agent_chat_history(session_id: str) -> list:
        """Get agent chat history from session db table by session id."""
        # newest top5
        session_dto: SessionDTO = SessionService().get_session_detail(session_id, 5)
        chat_history = []
        if session_dto:
            messages: List[MessageDTO] = session_dto.messages
            if len(messages) > 0:
                for message in messages:
                    content: str = message.content
                    if content is not None:
                        chat_history.extend(json.loads(content))
        return chat_history

    @staticmethod
    def add_agent_chat_history(agent_id: str, session_id: str,
                               input: str, output: str, cur_time: datetime) -> Tuple[str, int]:
        """Add agent chat history to session and message db tables."""
        content = json.dumps([{'type': 'human', 'content': input}, {'type': 'ai', 'content': output}],
                             ensure_ascii=False)
        session_id = SessionService.update_session(session_id, agent_id, cur_time)
        message_id = MessageService.add_message(session_id, content, cur_time)
        return session_id, message_id

    @staticmethod
    def assemble_agent_dto(agent: Agent, agent_dto: AgentDTO) -> AgentDTO:
        """Assemble agent dto from agent instance."""
        agent_model: AgentModel = agent.agent_model
        agent_dto.description = agent_model.info.get('description', '')
        agent_dto.prompt = AgentService.get_prompt_dto(agent_model)
        agent_dto.llm = AgentService.get_llm_dto(agent_model)
        agent_dto.memory = agent_model.memory.get('name', '')
        agent_dto.tool = AgentService.get_tool_dto_list(agent_model)
        agent_dto.knowledge = AgentService.get_knowledge_dto_list(agent_model)
        agent_dto.planner = AgentService.get_planner_dto(agent_model)
        return agent_dto

    @staticmethod
    def assemble_planner_members(planner: dict, member_keys: List[str]) -> List[AgentDTO]:
        """Assemble planner members by looking up the configured multi-agent groups in the planner.

        Args:
            planner (dict): The planner dictionary in agent configuration.
            member_keys (List[str]): The multi-agent member keys to look up in the planner.

        Returns:
            List[AgentDTO]: The list of agent DTOs representing the planner members.
        """
        members = []
        if not planner or not member_keys:
            return members

        for member_key in member_keys:
            current_value = planner
            # get the corresponding agent instances configured in the planner through member_keys
            for path in member_key.split('.'):
                if isinstance(current_value, dict) and path in current_value:
                    current_value = current_value[path]
                else:
                    current_value = None
                    break

            if not current_value:
                continue

            if isinstance(current_value, str):
                current_value = [current_value]

            if isinstance(current_value, list):
                for val in current_value:
                    # assemble each agent instance
                    agent: Agent = AgentManager().get_instance_obj(val)
                    product: Product = ProductManager().get_instance_obj(val)
                    if agent:
                        agent_dto = AgentDTO(id=val, nickname=product.nickname if product else '',
                                             avatar=product.avatar if product else '')
                        members.append(AgentService().assemble_agent_dto(agent, agent_dto))

        return members
