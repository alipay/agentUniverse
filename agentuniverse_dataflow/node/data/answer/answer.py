# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/6/16 19:19
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: answer.py
from agentuniverse_dataflow.node.data.base.prompt_answer_base import PromptAnswerBase
from agentuniverse_dataflow.util.llm.llm_call import batch_call


class AnswerNode(PromptAnswerBase):
    """The RewriteNode class, which is used to define the class of rewrite node."""

    def _node_process(self) -> None:
        if not self._prompt_answer_list or len(self._prompt_answer_list) == 0:
            return

        total_prompt_num = 0
        prompts = []
        prompt_list_num = len(self._prompt_answer_list)
        prompt_answer_list = self._prompt_answer_list
        self._prompt_answer_list = []
        for i in range(0, prompt_list_num):
            prompt = prompt_answer_list[i][0]
            prompts.append(prompt)
            total_prompt_num = total_prompt_num + 1
            if total_prompt_num % self._batch_prompt_size == 0:
                res = batch_call(prompts, self.llm)
                for prompt, answer in zip(prompts, res):
                    if res is not None:
                        self._prompt_answer_list.append((prompt, answer))
                    prompts = []
            else:
                if total_prompt_num == prompt_list_num and len(prompts) > 0:
                    res = batch_call(prompts, self.llm)
                    for prompt, answer in zip(prompts, res):
                        if res is not None:
                            self._prompt_answer_list.append((prompt, answer))
                    return
