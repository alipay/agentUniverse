from enum import Enum
from typing import List
from langchain.chains.summarize import load_summarize_chain
import asyncio
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from agentuniverse.llm.llm import LLM
from agentuniverse.llm.llm_manager import LLMManager
from agentuniverse.prompt.prompt_model import AgentPromptModel


class PromptProcessEnum(Enum):
    TRUNCATE = 'truncate'
    STUFF = 'stuff'
    MAP_REDUCE = 'map_reduce'

    @classmethod
    def from_value(cls, value):
        for member in cls:
            if member.value.lower() == value.lower():
                return member
        raise ValueError(f"No enum member with value: {value}")


summarize_prompt_template = """
写下这段文字的详细摘要，输出结果中需要涵盖文本的要点、数据以及任何重要的细节。
注意：结果输出时必须用中文。
{text}
"""

combine_prompt_template = """
写出以下由三重反引号分隔的文本的详细摘要，输出结果中需要涵盖文本的要点、数据以及任何重要的细节。
注意：结果输出时必须用中文。
```{text}```
"""

summarize_prompt = PromptTemplate(template=summarize_prompt_template, input_variables=["text"])
combine_prompt = PromptTemplate(template=combine_prompt_template, input_variables=["text"])


def summarize_by_stuff(texts: List[str], llm: LLM):
    """
    stuff summarization -- general method
    """
    stuff_chain = load_summarize_chain(llm.as_langchain(), chain_type='stuff', verbose=True, prompt=summarize_prompt)
    return asyncio.run(stuff_chain.arun([Document(page_content=text) for text in texts]))


def summarize_by_map_reduce(texts: List[str], llm: LLM, agent_llm: LLM):
    """
    map reduce summarization -- general method
    """
    texts = split_texts(texts, agent_llm)
    map_reduce_chain = load_summarize_chain(llm.as_langchain(), chain_type='map_reduce', verbose=True,
                                            map_prompt=summarize_prompt,
                                            combine_prompt=combine_prompt)
    return asyncio.run(map_reduce_chain.arun([Document(page_content=text) for text in texts]))


def split_text_on_tokens(text: str, text_token, chunk_size=800, chunk_overlap=100) -> List[str]:
    """Split incoming text and return chunks using tokenizer."""
    # Calculate the number of characters represented by each token.
    char_per_token = len(text) / text_token
    chunk_char_size = int(chunk_size * char_per_token)
    chunk_char_overlap = int(chunk_overlap * char_per_token)

    result = []
    current_position = 0

    while current_position + chunk_char_overlap < len(text):
        if current_position + chunk_char_size >= len(text):
            chunk = text[current_position:]
        else:
            chunk = text[current_position:current_position + chunk_char_size]

        result.append(chunk)
        current_position += chunk_char_size - chunk_char_overlap

    return result


def split_texts(texts: list[str], agent_llm: LLM, chunk_size=800, chunk_overlap=100, retry=True) -> list[str]:
    """
    split texts into chunks with the fixed token length -- general method
    """
    try:
        split_texts_res = []
        llm = agent_llm.as_langchain()
        for text in texts:
            text_token = llm.get_num_tokens(text)
            split_texts_res.extend(
                split_text_on_tokens(text=text, text_token=text_token, chunk_size=chunk_size,
                                     chunk_overlap=chunk_overlap))
        return split_texts_res
    except Exception as e:
        if retry:
            return split_texts(texts=texts, agent_llm=agent_llm, retry=False)
        raise ValueError("split text failed, exception=" + str(e))


def truncate_content(content: str, token_length: int, agent_llm: LLM) -> str:
    """
    truncate the content based on the llm token limit
    """
    return str(split_texts(texts=[content], chunk_size=token_length, agent_llm=agent_llm)[0])


def generate_template(agent_prompt_model: AgentPromptModel, prompt_assemble_order: list[str]) -> str:
    """Convert the agent prompt model to an ordered list.

    Args:
        agent_prompt_model (AgentPromptModel): The agent prompt model.
        prompt_assemble_order (list[str]): The prompt assemble ordered list.
    Returns:
        list: The ordered list.
    """
    values = []
    for attr in prompt_assemble_order:
        value = getattr(agent_prompt_model, attr, None)
        if value is not None:
            values.append(value)

    return "\n".join(values)


def process_llm_token(prompt_template: PromptTemplate, profile: dict, planner_input: dict):
    """Process the prompt template based on the prompt processor.

    Args:
        prompt_template (PromptTemplate): The prompt template.
        profile (dict): The profile.
        planner_input (dict): The planner input.
    """
    llm_model: dict = profile.get('llm_model')
    llm_name: str = llm_model.get('name')

    prompt_processor: dict = llm_model.get('prompt_processor') or dict()
    prompt_processor_type: str = prompt_processor.get('type') or PromptProcessEnum.TRUNCATE.value
    prompt_processor_llm: str = prompt_processor.get('llm') or llm_name
    prompt_input_dict = {key: planner_input[key] for key in prompt_template.input_variables if key in planner_input}

    agent_llm: LLM = LLMManager().get_instance_obj(llm_name)
    llm_max_tokens: int = agent_llm.max_tokens
    prompt_llm: LLM = LLMManager().get_instance_obj(prompt_processor_llm)

    prompt = prompt_template.format(**prompt_input_dict)
    prompt_token_length: int = len(prompt)

    if prompt_token_length <= llm_max_tokens:
        return

    remaining_token_length: int = prompt_token_length - llm_max_tokens

    process_prompt_type_enum = PromptProcessEnum.from_value(prompt_processor_type)

    content = planner_input.get('background')
    if process_prompt_type_enum == PromptProcessEnum.TRUNCATE:
        planner_input['background'] = truncate_content(content, remaining_token_length, agent_llm)
    elif process_prompt_type_enum == PromptProcessEnum.STUFF:
        planner_input['background'] = summarize_by_stuff([content], prompt_llm)
    elif process_prompt_type_enum == PromptProcessEnum.MAP_REDUCE:
        planner_input['background'] = summarize_by_map_reduce([content], prompt_llm, agent_llm)
