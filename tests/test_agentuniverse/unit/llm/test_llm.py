# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/3/21 14:55
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: test_llm.py
import asyncio
import unittest

from langchain.chains import ConversationChain

from agentuniverse.llm.openai_llm import OpenAILLM


class LLMTest(unittest.TestCase):
    """
    Test cases for LLM class
    """

    def setUp(self) -> None:
        self.llm = OpenAILLM(model_name='gpt-4')

    def test_call(self) -> None:
        messages = [
            {
                "role": "user",
                "content": "hi, please introduce yourself",
            }
        ]
        output = self.llm.call(messages=messages,streaming=False)
        print(output.__str__())

    def test_acall(self) -> None:
        messages = [
            {
                "role": "user",
                "content": "hi, please introduce yourself",
            }
        ]
        output = asyncio.run(self.llm.acall(messages=messages,streaming=False))
        print(output.__str__())

    def test_call_stream(self):
        messages = [
            {
                "role": "user",
                "content": "hi, please introduce yourself",
            }
        ]
        for chunk in self.llm.call(messages=messages, streaming=True):
            print(chunk.text, end='')
        print()

    #
    def test_acall_stream(self):
        messages = [
            {
                "role": "user",
                "content": "hi, please introduce yourself",
            }
        ]
        asyncio.run(self.call_stream(messages=messages))

    #
    async def call_stream(self, messages: list):

        async for chunk in await self.llm.acall(messages=messages, streaming=True):
            print(chunk, end='')
        print()

    def test_as_langchain(self):
        langchain_llm = self.llm.as_langchain()
        llm_chain = ConversationChain(llm=langchain_llm)
        res = llm_chain.predict(input='hello')
        print(res)


if __name__ == '__main__':
    unittest.main()
