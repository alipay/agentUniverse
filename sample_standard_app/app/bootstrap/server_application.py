# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/4/8 20:58
# @Author  : jerry.zzw 
# @Email   : jerry.zzw@antgroup.com
# @FileName: server_application.py
from agentuniverse.agent_serve.web.web_booster import start_web_server
from agentuniverse.base.agentuniverse import AgentUniverse


class ServerApplication:
    """
    Server application.
    """

    @classmethod
    def start(cls):
        AgentUniverse().start()
        start_web_server()


if __name__ == "__main__":
    from langchain_community.document_loaders import AsyncHtmlLoader

    urls = ["https://www.espn.com", "https://lilianweng.github.io/posts/2023-06-23-agent/"]
    loader = AsyncHtmlLoader(urls)
    docs = loader.load()
    print(docs)
# ServerApplication.start()
