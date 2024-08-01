# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/26 13:37
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: product_platform.py
from typing import List

from agentuniverse.base.agentuniverse import AgentUniverse
from agentuniverse_product.agentuniverse_product import AgentUniverseProduct
from agentuniverse_product.service.agent_service.agent_service import AgentService
from agentuniverse_product.service.llm_service.llm_service import LLMService
from agentuniverse_product.service.model.agent_dto import AgentDTO
from agentuniverse_product.service.model.llm_dto import LlmDTO
from agentuniverse_product.service.model.session_dto import SessionDTO
from agentuniverse_product.service.model.tool_dto import ToolDTO
from agentuniverse_product.service.session_service.session_service import SessionService
from agentuniverse_product.service.tool_service.tool_service import ToolService

AgentUniverse().start(config_path='../../config/config.toml')
AgentUniverseProduct().start(config_path='../../config/config.toml')

if __name__ == '__main__':
    SessionService().create_session('demo_peer_agent')
    session_list: List[SessionDTO] = SessionService.get_session_list('demo_peer_agent')
    for chunk in AgentService().stream_chat('demo_peer_agent', session_list[0].id,
                                            '巴菲特为什么减持比亚迪'):
        print(chunk)
    print('----------------------------------')

    agent_list: List[AgentDTO] = AgentService.get_agent_list()

    session: SessionDTO = SessionService().get_session_detail(session_list[0].id)

    llm = LlmDTO(id='qwen_llm', model_name=['qwen-max'], temperature=0.4)
    agent_dto = AgentDTO(opening_speech='aaa', id='demo_rag_agent', llm=llm)
    AgentService.update_agent(agent_dto)

    agent_dto: AgentDTO = AgentService.get_agent_detail('demo_rag_agent')

    tool_list: List[ToolDTO] = ToolService.get_tool_list()

    llm_list: List[LlmDTO] = LLMService.get_llm_list()
