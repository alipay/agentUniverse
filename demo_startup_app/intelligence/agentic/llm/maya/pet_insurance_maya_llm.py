# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/5/7 15:46
# @Author  : weizjajj 
# @Email   : weizhongjie.wzj@antgroup.com
# @FileName: ant_maya_llm.py
import json
from typing import Any, Optional, List, Union, Iterator

import requests
import tiktoken
from agentuniverse.base.annotation.trace import trace_llm
from agentuniverse_ant_ext.llm.langchian_instance.langchain_instance import LangChainInstance
from langchain_core.callbacks import AsyncCallbackManagerForLLMRun
from langchain_core.language_models import BaseLanguageModel

from agentuniverse.base.config.component_configer.configers.llm_configer import LLMConfiger
from agentuniverse.base.util.logging.logging_util import LOGGER
from agentuniverse.llm.llm import LLM
from agentuniverse.llm.llm_output import LLMOutput


class PetInsuranceMayaLLM(LLM):
    model_name: Optional[str] = "AntGLM"
    sceneName: Optional[str] = None
    chainName: Optional[str] = None
    publishDomain: Optional[str] = None
    serviceId: Optional[str] = None
    message_id: str = 'default'
    endpoint: str = "xxx"
    streaming: Optional[bool] = False
    # max tokens to generate
    max_tokens: int = 1024
    # max content length
    max_length: int = 4096
    streaming_full: bool = True
    params_filed: str = "data"
    query_field: str = "query"
    scene_code: Optional[str] = None

    @trace_llm
    def call(self, *args: Any, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        """
        Call the model on the inputs.
        """
        streaming = kwargs.pop("streaming") if "streaming" in kwargs else self.streaming
        kwargs["streaming"] = streaming
        if not streaming:
            return self.no_streaming_call(*args, **kwargs)
        else:
            return self.streaming_call(*args, **kwargs)

    @staticmethod
    def parse_output(result: dict) -> LLMOutput:
        """
        Parse the output of the model.
        """
        if "data" in result:
            if "output_string" in result["data"]:
                text = result["data"]["output_string"]
            elif "result" in result["data"]:
                text = result["data"]["result"]
            else:
                text = result["data"]["out_string"]
        elif "result" in result:
            if "output_string" in result["result"]:
                text = result["result"]["output_string"]
            elif "result" in result["result"]:
                text = result["result"]["result"]
            else:
                text = result["result"]["out_string"]
        else:
            raise ValueError("No output found in response.")
        return LLMOutput(text=text, raw=result)

    @staticmethod
    def parse_stream_output(line: bytes, cursor: int) -> tuple[None, int] | tuple[LLMOutput, int]:
        """
        Parse the output of the model.
        """
        line = line.decode("utf-8")
        if not line or "out_string" not in line:
            return None, cursor
        line_json = json.loads(line)
        line_json['out_string'] = line_json['out_string'][cursor:]
        size = len(line_json["out_string"])
        cursor += size
        return LLMOutput(text=line_json["out_string"], raw=line_json), cursor

    def _call(self, *args: Any, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        return self.call(*args, **kwargs)

    async def _acall(self, *args: Any, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        return await self.acall(*args, **kwargs)

    def as_langchain(self) -> BaseLanguageModel:
        """
        Return the LangChain representation of this LLM.
        """
        return LangChainInstance(streaming=self.streaming, llm=self, llm_type="Maya")

    def max_context_length(self) -> int:
        """Max context length.

          The total length of input tokens and generated tokens is limited by the openai model's context length.
          """
        return self.max_length

    def get_num_tokens(self, text: str) -> int:
        """Get the number of tokens present in the text.

        Useful for checking if an input will fit in an openai model's context window.

        Args:
            text: The string input to tokenize.

        Returns:
            The integer number of tokens in the text.
        """

        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))

    def request_stream_data(self, prompt: str, stop: str = ''):
        return {
            "sceneName": self.sceneName,
            "sceneCode": self.scene_code,
            "chainName": self.chainName,
            "publishDomain": self.publishDomain,
            "serviceId": self.serviceId,
            "features": {self.params_filed: json.dumps({self.query_field: prompt, "sync": False}),
                         "temperature": self.temperature,
                         "stop_words": stop,
                         "max_output_length": self.max_length},
        }

    def request_data(self, prompt: str, stop: str = None):
        return {
            "sceneName": self.sceneName,
            "sceneCode": self.scene_code,
            "chainName": self.chainName,
            "publishDomain": self.publishDomain,
            "serviceId": self.serviceId,
            "features": {self.params_filed: json.dumps({self.query_field: prompt, "sync": False}),
                         "temperature": self.temperature,
                         "stop_words": stop,
                         "max_output_length": self.max_length},
        }

    def no_streaming_call(self,
                          prompt: str,
                          stop: Optional[List[str]] = None,
                          run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
                          **kwargs) -> LLMOutput:
        suffix = f"?sceneCode={self.scene_code}&model_name={self.model_name}" \
            if self.scene_code else f"?model_name={self.model_name}"
        # 同步http包发送http请求
        resp = requests.post(
            url=self.endpoint + suffix,
            headers={"Content-Type": "application/json"},
            data=json.dumps(self.request_data(prompt, stop[0] if stop else ''), ensure_ascii=False).encode("utf-8"),
            timeout=self.request_timeout,
        )
        resp = resp.json()
        try:
            if resp and resp["success"]:
                return self.parse_output(resp)
            else:
                LOGGER.debug("请求ChatGLM失败:", resp)
                raise Exception(resp)
        except Exception as e:
            LOGGER.exception("请求ChatGLM失败")
            raise e

    def streaming_call(self,
                       prompt: str,
                       stop: Optional[List[str]] = None,
                       run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
                       **kwargs):
        suffix = f"?sceneCode={self.scene_code}&model_name={self.model_name}" \
            if self.scene_code else f"?model_name={self.model_name}"
        # 异步http包发送http请求
        with requests.post(
                url=self.endpoint + suffix,
                data=json.dumps(self.request_stream_data(prompt, stop[0] if stop else ''), ensure_ascii=False).encode(
                    "utf-8"),
                timeout=self.request_timeout,
                headers={"Content-Type": "application/json"},
                stream=True
        ) as resp:
            cursor = 0
            for line in resp.iter_lines():
                if not self.streaming_full:
                    cursor = 0
                output, cursor = self.parse_stream_output(line, cursor)
                if output:
                    yield output

    def set_by_agent_model(self, **kwargs) -> 'AntMayaLLM':
        copied_obj = super().set_by_agent_model(**kwargs)
        """Set the parameters of the agent model."""
        if "ext_info" in kwargs:
            ext_info = kwargs.get("ext_info", self.ext_info)
            if "sceneName" in ext_info:
                copied_obj.sceneName = ext_info.get("sceneName", self.sceneName)
            if "chainName" in ext_info:
                copied_obj.chainName = ext_info.get("chainName", self.chainName)
            if "publishDomain" in ext_info:
                copied_obj.publishDomain = ext_info.get("publishDomain", self.publishDomain)
            if "serviceId" in ext_info:
                copied_obj.serviceId = ext_info.get("serviceId", self.serviceId)
            if "endpoint" in ext_info:
                copied_obj.endpoint = ext_info.get("endpoint", self.endpoint)
            if "max_length" in ext_info:
                copied_obj.max_length = ext_info.get("max_length", self.max_length)
            if "params_filed" in ext_info:
                copied_obj.params_filed = ext_info.get("params_filed", self.params_filed)
            if "query_field" in ext_info:
                copied_obj.query_field = ext_info.get("query_field", self.query_field)
        return copied_obj

    def initialize_by_component_configer(self, configer: LLMConfiger):
        """Initialize the agent model by component configer."""
        self.scene_code = configer.configer.value.get('scene_code', None)
        ext_info = configer.ext_info
        if not ext_info:
            return super().initialize_by_component_configer(configer)
        if "sceneName" in ext_info:
            self.sceneName = ext_info["sceneName"]
        if "chainName" in ext_info:
            self.chainName = ext_info["chainName"]
        if "publishDomain" in ext_info:
            self.publishDomain = ext_info["publishDomain"]
        if "serviceId" in ext_info:
            self.serviceId = ext_info["serviceId"]
        if "endpoint" in ext_info:
            self.endpoint = ext_info["endpoint"]
        if "max_length" in ext_info:
            self.max_length = ext_info["max_length"]
        if "params_filed" in ext_info:
            self.params_filed = ext_info["params_filed"]
        if "query_field" in ext_info:
            self.query_field = ext_info["query_field"]
        if "streaming_full" in ext_info:
            self.streaming_full = ext_info["streaming_full"]
        super().initialize_by_component_configer(configer)
        return self
