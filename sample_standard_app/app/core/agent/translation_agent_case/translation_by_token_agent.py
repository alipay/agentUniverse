# !/usr/bin/env python3
# -*- coding:utf-8 -*-
from langchain_text_splitters import RecursiveCharacterTextSplitter

# @Time    : 2024/6/25 16:56
# @Author  : weizjajj 
# @Email   : weizhongjie.wzj@antgroup.com
# @FileName: translation_planner.py

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.input_object import InputObject
from agentuniverse.llm.llm import LLM
from agentuniverse.llm.llm_manager import LLMManager


def calculate_chunk_size(token_count: int, token_limit: int) -> int:
    """
    Calculate the chunk size based on the token count and token limit.

    Args:
        token_count (int): The total number of tokens.
        token_limit (int): The maximum number of tokens allowed per chunk.

    Returns:
        int: The calculated chunk size.

    Description:
        This function calculates the chunk size based on the given token count and token limit.
        If the token count is less than or equal to the token limit, the function returns the token count as the chunk size.
        Otherwise, it calculates the number of chunks needed to accommodate all the tokens within the token limit.
        The chunk size is determined by dividing the token limit by the number of chunks.
        If there are remaining tokens after dividing the token count by the token limit,
        the chunk size is adjusted by adding the remaining tokens divided by the number of chunks.

    Example:
        >>> calculate_chunk_size(1000, 500)
        500
        >>> calculate_chunk_size(1530, 500)
        389
        >>> calculate_chunk_size(2242, 500)
        496
    """

    if token_count <= token_limit:
        return token_count

    num_chunks = (token_count + token_limit - 1) // token_limit
    chunk_size = token_count // num_chunks

    remaining_tokens = token_count % token_limit
    if remaining_tokens > 0:
        chunk_size += remaining_tokens // num_chunks

    return chunk_size


class TranslationAgent(Agent):
    def input_keys(self) -> list[str]:
        return self.agent_model.profile.get('input_keys')

    def output_keys(self) -> list[str]:
        return self.agent_model.profile.get('output_keys')

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        for key in self.input_keys():
            agent_input[key] = input_object.get_data(key)
        return agent_input

    def parse_result(self, planner_result: dict) -> dict:
        return planner_result

    def execute(self, input_object: InputObject, agent_input: dict) -> dict:
        llm_name = self.agent_model.profile.get('llm_model').get('name')
        llm: LLM = LLMManager().get_instance_obj(llm_name)
        source_text = agent_input.get('source_text')
        text_tokens = llm.get_num_tokens(source_text)
        # 这里使用最大输入token，因为必须要保证有足够的token输出翻译结果
        max_context_length = llm.max_tokens
        if text_tokens < max_context_length:
            return super().execute(input_object, agent_input)

        chunk_result = list[str]()
        chunk_size = calculate_chunk_size(text_tokens, max_context_length)
        source_text_chunks = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=0).split_text(
            source_text)

        input_object.add_data('work_agent', 'multi_translation_work_agent')
        input_object.add_data('reflection_agent', 'multi_reflection_translation_work_agent')
        input_object.add_data('improve_agent', 'multi_improve_translation_work_agent')

        for i in range(len(source_text_chunks)):
            tagged_text = ""
            if i - 1 > 0:
                tagged_text += source_text_chunks[i - 1]
            tagged_text += (
                    "<TRANSLATE_THIS>"
                    + source_text_chunks[i]
                    + "</TRANSLATE_THIS>"
            )
            if i + 1 < len(source_text_chunks):
                tagged_text += source_text_chunks[i + 1]
            agent_input['chunk_to_translate'] = source_text_chunks[i]
            agent_input['tagged_text'] = tagged_text
            result = super().execute(input_object, agent_input)
            chunk_result.append(result.get('output'))

        return {
            'output': "".join(chunk_result)
        }
