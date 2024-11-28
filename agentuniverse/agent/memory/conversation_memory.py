# !/usr/bin/env python3
# -*- coding:utf-8 -*-
import asyncio
# @Time    : 2024/11/21 16:55
# @Author  : weizjajj 
# @Email   : weizhongjie.wzj@antgroup.com
# @FileName: trace_memory.py

import json
import queue
import traceback
import uuid
from threading import Thread
from typing import List

from agentuniverse.agent.action.knowledge.store.document import Document

from agentuniverse.agent.memory.memory_manager import MemoryManager
from agentuniverse.agent.memory.message import Message
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.base.annotation.singleton import singleton
from agentuniverse.base.context.framework_context_manager import FrameworkContextManager
from agentuniverse.base.util.logging.logging_util import LOGGER


@singleton
class ConversationMemory:
    """
    1. 采集memory调度信息
    """

    def __init__(self):
        self.queue = queue.Queue(1000)
        Thread(target=self._consume_queue, daemon=True).start()

    def _consume_queue(self):
        while True:
            func = self.queue.get()
            try:
                func()
            except Exception as e:
                LOGGER.error(f"Failed to process trace info: {e}")
                # 打印详细堆栈信息
                traceback.print_exc()
            finally:
                self.queue.task_done()

    def query_agent_memory(self, agent_id: str, top_k: int = 50, memory_name: str = None, session_id=None):
        if memory_name is None:
            memory_name = FrameworkContextManager().get_context('conversation_memory')
        if session_id is None:
            session_id = FrameworkContextManager().get_context('session_id')
            if session_id is None:
                return []

        conversation_memory: 'Memory' = MemoryManager().get_instance_obj(memory_name)
        messages: List[Message] = conversation_memory.get_with_no_prune(session_id=session_id, top_k=top_k)
        res = []
        for message in messages:
            content = json.loads(message.content)
            if message.type == "input" and content['target'] == agent_id and content['target_type'] == 'agent':
                message.content = content.get('content')
                res.append(message)
            if message.type == "output" and content['source'] == agent_id and content['source_type'] == 'agent':
                message.content = content.get('content')
                res.append(message)
        return res

    def generate_relation_str(self, source: str, target: str, source_type: str, target_type: str, type: str):

        if source_type == 'agent' and target_type == 'agent' and type == 'input':
            return f"智能体 {source} 向智能体 {target} 提出了一个问题"
        if source_type == 'agent' and target_type == 'agent' and type == 'output':
            return f"智能体 {source} 回答了智能体 {target} 的问题"
        if source_type == 'agent' and target_type == 'tool' and type == 'input':
            return f"智能体 {source} 调用了工具 {target}，执行的参数是"
        if source_type == 'tool' and target_type == 'agent' and type == 'output':
            return f"工具 {source} 返回给给智能体 {target} 的执行结果"
        if source_type == 'agent' and target_type == 'knowledge' and type == 'input':
            return f"智能体 {source} 在知识库 {target} 中进行了搜索，关键词是"
        if source_type == 'knowledge' and target_type == 'agent' and type == 'output':
            return f"知识库 {source} 返回给给智能体 {target} 的搜索结果"
        if source_type == 'agent' and target_type == 'llm' and type == 'input':
            return f"智能体 {source} 向大模型 {target} 提问"
        if source_type == 'llm' and target_type == 'agent' and type == 'output':
            return f"大模型 {source} 返回给智能体 {target} 的答案"
        if source_type == 'unknown' and target_type == 'agent' and type == 'input':
            return f"未知类型 {source} 向智能体 {target} 提出了一个问题"
        if source_type == 'agent' and target_type == 'unknown' and type == 'output':
            return f"智能体 {source} 回答了未知 {target} 的问题"
        if source_type == "user" and target_type == 'agent' and type == 'input':
            return f"用户向智能体 {target} 提出了一个问题"
        if source_type == 'agent' and target_type == 'user' and type == 'output':
            return f"智能体 {source} 回答了用户的问题"
        return None

    def generate_relation_str_en(self, source: str, target: str, source_type: str, target_type: str, type: str):
        if source_type == 'agent' and target_type == 'agent' and type == 'input':
            return f"Agent {source} asked a question to agent {target}"
        if source_type == 'agent' and target_type == 'agent' and type == 'output':
            return f"Agent {source} answered the question asked by agent {target}"
        if source_type == 'agent' and target_type == 'tool' and type == 'input':
            return f"Agent {source} called tool {target}, the parameters are"
        if source_type == 'tool' and target_type == 'agent':
            return f"Tool {source} returned the result to agent {target}"
        if source_type == 'agent' and target_type == 'knowledge' and type == 'input':
            return f"Agent {source} searched in knowledge {target}, the keywords are"
        if source_type == 'knowledge' and target_type == 'agent' and type == 'output':
            return f"Knowledge {source} returned the result to agent {target}"
        if source_type == 'agent' and target_type == 'llm' and type == 'input':
            return f"Agent {source} asked a question to llm {target}"
        if source_type == 'llm' and target_type == 'agent' and type == 'output':
            return f"LLM {source} returned the answer to agent {target}"
        if source_type == 'unknown' and target_type == 'agent' and type == 'input':
            return f"Unknown type {source} asked a question to agent {target}"
        if source_type == 'agent' and target_type == 'unknown' and type == 'output':
            return f"Agent {source} answered the unknown {target} question"
        if source_type == "user" and target_type == 'agent' and type == 'input':
            return f"User asked a question to agent {target}"
        if source_type == 'agent' and target_type == 'user' and type == 'output':
            return f"Agent {source} answered the user's question"
        return None

    def _add_trace_info(self, source: str,
                        source_type: str,
                        target: str,
                        target_type: str,
                        type: str,
                        params: dict, **kwargs) -> None:
        if type in params:
            content = params[type]
        else:
            try:
                content = json.dumps(params, ensure_ascii=False)
            except Exception as e:
                content = str(e)
        language = kwargs.get('language', 'en')
        if language == 'zh':
            prefix = self.generate_relation_str(source, target, source_type, target_type, type)
        else:
            prefix = self.generate_relation_str_en(source, target, source_type, target_type, type)
        if not prefix:
            return
        memory = MemoryManager().get_instance_obj(kwargs.get('conversation_memory'))
        if memory:
            message = Message(
                content=json.dumps(
                    {
                        "content": f"{prefix}:{content}",
                        "source": source,
                        "source_type": source_type,
                        "target": target,
                        "target_type": target_type,
                        "type": type
                    },ensure_ascii=False
                ),
                metadata={'session_id': kwargs.get('session_id')},
                source=kwargs.get('trace_id'),
                type=type,
            )
            memory.add([message], session_id=kwargs.get('session_id'))
        LOGGER.info(f"{kwargs.get('conversation_memory')} | {kwargs.get('trace_id')} | {prefix}:{content}")

    def _add_trace(self, start_info, target_info: dict, type: str, params: dict, session_id: str, trace_id: str,
                   conversation_memory: str, language: str):
        if "kwargs" in params:
            params = params['kwargs']
        if params is str:
            params = {
                type: params
            }
        kwargs = {'source': start_info['source'], 'source_type': start_info['type'], 'target': target_info['source'],
                  'target_type': target_info['type'], 'type': type, 'params': params, 'trace_id': trace_id,
                  'session_id': session_id, 'conversation_memory': conversation_memory}
        self._add_trace_info(**kwargs)

    def add_trace_info(self, start_info: dict, target_info: dict, type: str, params: dict):
        """Add trace info to the memory."""
        conversation_memory = FrameworkContextManager().get_context('conversation_memory')
        if not conversation_memory:
            return
        trace_id = FrameworkContextManager().get_context('trace_id')
        if trace_id is None:
            trace_id = str(uuid.uuid4())
            FrameworkContextManager().set_context('trace_id', trace_id)

        session_id = FrameworkContextManager().get_context('session_id')
        if session_id is None:
            session_id = str(uuid.uuid4())
            FrameworkContextManager().set_context('session_id', session_id)

        language = FrameworkContextManager().get_context('language', "en")

        def add_trace():
            self._add_trace(start_info, target_info, type, params, session_id, trace_id, conversation_memory, language)

        self.queue.put_nowait(add_trace)

    def add_tool_input_info(self, start_info: dict, target: str, params: dict):
        """Add trace info to the memory."""
        target_info = {'source': target, 'type': 'tool'}
        self.add_trace_info(start_info, target_info, 'input', params)

    def add_tool_output_info(self, start_info: dict, target: str, params: dict):
        """Add trace info to the memory."""
        target_info = {'source': target, 'type': 'tool'}
        self.add_trace_info(target_info, start_info, 'output', params)

    def add_agent_input_info(self, start_info: dict, instance: 'Agent', params: dict):
        target_info = {'source': instance.agent_model.info.get('name'), 'type': 'agent'}
        self.add_trace_info(start_info, target_info, 'input', params)

    def add_knowledge_input_info(self, start_info: dict, target: str, params: dict):
        target_info = {'source': target, 'type': 'knowledge'}
        self.add_trace_info(start_info, target_info, 'input', params)

    def add_knowledge_output_info(self, start_info: dict, target: str, params: List[Document]):
        target_info = {'source': target, 'type': 'knowledge'}
        doc_data = []
        for doc in params:
            doc_data.append(doc.text)
        self.add_trace_info(target_info, start_info, 'output', {
            'output': "\n==============================\n".join(doc_data)
        })

    def add_agent_result_info(self, agent_instance: 'Agent', agent_result: OutputObject, target_info: dict):
        conversation_memory = FrameworkContextManager().get_context('conversation_memory')
        if not conversation_memory:
            return

        trace_id = FrameworkContextManager().get_context('trace_id')
        session_id = FrameworkContextManager().get_context('session_id')
        language = FrameworkContextManager().get_context('language')

        def add_trace():
            output_keys = agent_instance.output_keys()
            params = {}
            for key in output_keys:
                params[key] = agent_result.get_data(key)
            start_info = {
                "source": agent_instance.agent_model.info.get('name'),
                "type": "agent"
            }
            self._add_trace(start_info, target_info, 'output', params, session_id, trace_id, conversation_memory,
                            language)

        self.queue.put_nowait(add_trace)

    def add_llm_input_info(self, start_info: dict, target: str, prompt: str):
        target_info = {'source': target, 'type': 'llm'}
        self.add_trace_info(start_info, target_info, 'input', {'input': prompt})

    def add_llm_output_info(self, start_info: dict, target: str, output: str):
        target_info = {'source': target, 'type': 'llm'}
        self.add_trace_info(target_info, start_info, 'output', {
            'output': output
        })
