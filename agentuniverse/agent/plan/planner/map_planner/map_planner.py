# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/4/28 14:44
# @Author  : weizjajj
# @Email   : weizhongjie.wzj@antgroup.com
# @FileName: map_planner.py

import asyncio
from typing import List

from langchain.chains import LLMChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.memory import BaseMemory
from langchain_core.documents import Document as LangDocument

from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.agent_model import AgentModel
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.plan.planner.planner import Planner
from agentuniverse.llm.llm import LLM
from agentuniverse.prompt.prompt import Prompt
from agentuniverse.prompt.prompt_manager import PromptManager
from agentuniverse.prompt.prompt_model import AgentPromptModel


class MapPlanner(Planner):
    """
    Map planner.
    """

    def invoke(self, agent_model: AgentModel, planner_input: dict,
               input_object: InputObject) -> dict:
        """Invoke the planner.

        Args:
            agent_model (AgentModel): Agent model object.
            planner_input (dict): Planner input object.
            input_object (InputObject): Agent input object.
        Returns:
            dict: The planner result.
        """
        # 1. load memory
        memory: BaseMemory = self.handle_memory(agent_model, planner_input)
        # 2. add tool background
        self.handle_all_actions(agent_model, planner_input, input_object)
        # 2.1 load llm and prompt
        if input_object.get_data('agent_model'):
            llm: LLM = self.handle_llm(input_object.get_data('agent_model'))
        else:
            llm: LLM = self.handle_llm(agent_model)
        # 2.2 load prompt
        prompt = self.handle_prompt(agent_model, planner_input)

        # 2.3 build chain
        llm_chain = LLMChain(llm=llm.as_langchain(),
                             prompt=prompt.as_langchain(),
                             output_key=self.output_key, memory=memory)
        map_docs = input_object.get_data('docs')
        # 3. conv to document
        if not map_docs:
            return {}
        elif type(map_docs) is str:
            map_docs = [Document(text=map_docs, metadata={}).as_langchain()]
        elif type(map_docs) is list:
            temp = []
            for doc in map_docs:
                if type(doc) is str:
                    temp.append(Document(text=doc, metadata={}).as_langchain())
                elif type(doc) is Document:
                    temp.append(doc.as_langchain())
                elif type(doc) is LangDocument:
                    temp.append(doc)
            map_docs = temp

        # 4. calculator the chunk size
        map_docs = self.split_docs(map_docs, llm, planner_input, prompt)

        # 5. do map summarize
        # get sem
        sem = agent_model.profile.get('sem')
        map_results = asyncio.run(self.map_docs_async(llm_chain, map_docs, planner_input, sem=sem))
        result = []
        # 6. package doc metadata
        for index, map_result in enumerate(map_results):
            result.append({
                'metadata': map_docs[index].metadata,
                'result': map_result
            })
        return {'output': result}

    def split_docs(self, docs: List[Document], llm: LLM, planner_input: dict, prompt: Prompt) -> List[Document]:
        text_token = 0
        text_size = 0
        if planner_input['background']:
            text_token += llm.get_num_tokens(planner_input['background'])
            text_size += len(planner_input['background'])
        text_token += llm.get_num_tokens(prompt.prompt_template)
        text_size += len(prompt.prompt_template)
        char_per_token = text_size / text_token
        chunk_token_size = llm.max_context_length() - text_token - llm.max_tokens
        chunk_size = char_per_token * chunk_token_size
        map_docs = RecursiveCharacterTextSplitter(chunk_size=chunk_size,
                                                  chunk_overlap=200).split_documents(docs)
        return map_docs

    @staticmethod
    async def map_docs_async(llm_chain: LLMChain, map_docs: List[Document], planner_input: dict, sem=3):
        """Map docs async."""
        # create a semaphore or use default value
        if sem is None or sem < 1:
            sem = 3
        semaphore = asyncio.Semaphore(sem)

        async def process_doc(doc):
            # use the semaphore to limit the number of concurrent requests
            async with semaphore:
                inputs = planner_input.copy()
                if inputs.get('background'):
                    inputs['background'] += '\n' + doc.page_content
                else:
                    inputs['background'] = doc.page_content
                # add doc metadata to inputs
                for k, v in doc.metadata.items():
                    inputs[k] = v
                return await llm_chain.acall(inputs=inputs)

        # create a list of tasks
        tasks = [process_doc(doc) for doc in map_docs]
        # wait for all tasks to complete
        return await asyncio.gather(*tasks)

    def handle_prompt(self, agent_model: AgentModel, planner_input: dict) -> Prompt:
        """Prompt module processing.

        Args:
            agent_model (AgentModel): Agent model object.
            planner_input (dict): Planner input object.
        Returns:
            Prompt: The prompt instance.
        """
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
