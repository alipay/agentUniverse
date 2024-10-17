# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/9/29 15:48
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: agent_util.py
from queue import Queue

from agentuniverse.agent.agent_model import AgentModel
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.memory.memory_manager import MemoryManager
from agentuniverse.agent.memory.message import Message
from agentuniverse.base.util.memory_util import generate_messages, get_memory_string
from agentuniverse.llm.llm import LLM
from agentuniverse.llm.llm_manager import LLMManager


def handle_memory(agent_model: AgentModel, agent_input: dict) -> Memory | None:
    """Get the memory instance and add the temporary messages to it.

    Args:
        agent_model (AgentModel): The agent model instance.
        agent_input (dict): Agent input object.

    Returns:
        Memory | None: The memory instance.
    """
    chat_history: list = agent_input.get('chat_history')
    memory_name = agent_model.memory.get('name')

    # get memory instance
    memory: Memory = MemoryManager().get_instance_obj(component_instance_name=memory_name)
    if memory is None:
        return None

    # generate a list of temporary messages from the given chat history and add them to the memory instance.
    temporary_messages: list[Message] = generate_messages(chat_history)
    if temporary_messages:
        memory.add(temporary_messages, **agent_input)

    llm_name = agent_model.profile.get('llm_model', {}).get('name')
    llm: LLM = LLMManager().get_instance_obj(llm_name)

    params: dict = dict()
    params['llm'] = llm
    params['agent_llm_name'] = llm_name
    return memory.set_by_agent_model(**params)


def handle_llm(agent_model: AgentModel) -> LLM:
    llm_name = agent_model.profile.get('llm_model', {}).get('name')
    llm: LLM = LLMManager().get_instance_obj(llm_name)
    return llm


def assemble_memory_input(memory: Memory, agent_input: dict) -> list[Message]:
    """Assemble memory intput variable.

    Args:
        memory (Memory): The memory instance.
        agent_input (dict): Agent input object.

    Returns:
        list[Message]: The memory messages.
    """
    memory_messages = []
    if memory:
        # get the memory messages from the memory instance.
        memory_messages = memory.get(**agent_input)
        # convert the memory messages to a string and add it to the agent input object.
        memory_str = get_memory_string(memory_messages)
        agent_input[memory.memory_key] = memory_str
    return memory_messages


def assemble_memory_output(memory: Memory, agent_input: dict,
                           content: str, source: str = None, memory_messages=None) -> \
        list[Message]:
    """Assemble memory output variable.

    Args:
        memory (Memory): The memory instance.
        agent_input (dict): Agent input object.
        content (str): The content of the current memory message.
        source (str): The source of the current memory message.
        memory_messages (List[Message]): The memory history messages.
    Returns:
        list[Message]: The assembled memory history messages.
    """
    cur_memory_message = Message(content=content, source=source)
    if memory:
        # add the current memory message to the memory instance.
        memory.add([cur_memory_message], **agent_input)
    if memory_messages is None:
        memory_messages = []
    memory_messages.append(cur_memory_message)
    return memory_messages


def stream_output(input_object: InputObject, data: dict):
    """Add data to the output stream.

    Args:
        input_object (InputObject): Agent input object.
        data (dict): The data to be streamed.
    """
    output_stream: Queue = input_object.get_data('output_stream', None)
    if output_stream is None:
        return
    output_stream.put_nowait(data)
