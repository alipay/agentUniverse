# agentUniverse
****************************************
语言版本: [English](./README.md) | [中文](./README_zh.md)

![](https://img.shields.io/badge/framework-agentUniverse-pink)
![](https://img.shields.io/badge/python-3.10%2B-blue?logo=Python)
[![](https://img.shields.io/badge/%20license-Apache--2.0-yellow)](LICENSE)
[![Static Badge](https://img.shields.io/badge/pypi-v0.0.4-blue?logo=pypi)](https://pypi.org/project/agentUniverse/)

![](docs/guidebook/_picture/logo_bar.jpg)
****************************************

## 项目介绍

本框架是一个大模型多智能体框架。核心提供了多智能体协作编排组件，其相当于一个模式工厂（pattern factory），允许开发者对多智能体协作模式进行开发定制，同时附带了搭建单一智能体的全部关键组件。开发者可以基于本框架轻松构建多智能体应用，并通过社区对不同领域的pattern实践进行交流共享。

框架将预置有若干已在真实产业中验证有效的多智能体协作模式组件，并在未来持续丰富。目前即将开放的模式组件包括：

- PEER 模式组件：
该pattern通过计划（Plan）、执行（Execute）、表达（Express）、评价（Review）四个不同职责的智能体，实现对复杂问题的多步拆解、分步执行，并基于评价反馈进行自主迭代，最终提升推理分析类任务表现。典型适用场景：事件解读、行业分析


- DOE 模式组件：
该pattern通过数据精制（Data-fining）、观点注入（Opinion-inject）、表达（Express）三个智能体，实现对数据密集、高计算精度、融合专家观点的生成任务的效果提升。典型适用场景：财报生成

更多模式组件持续推出中...

![](docs/guidebook/_picture/agent_universe_framework_resize.jpg)


## agentUniverse 示例项目
[agentUniverse 示例项目](sample_standard_app/README_zh.md)

## 快速安装
使用pip：
```shell
pip install agentUniverse
```

## 快速开始
我们将向您展示如何：
* 进行环境与应用工程准备
* 构建一个简单的agent
* 使用模式组件完成多agent协同
* 对agent执行效果进行测试调优
* 对agent进行快速服务化

详情请阅读[快速开始](docs/guidebook/zh/1_3_%E5%BF%AB%E9%80%9F%E5%BC%80%E5%A7%8B.md) 。

## 用户指南
更多详细信息，请参阅[指南](docs/guidebook/zh/0_%E7%9B%AE%E5%BD%95.md) 。

## API 参考
[readthedocs](https://agentuniverse.readthedocs.io/en/latest/)

## 更多方式联系我们
* github: https://github.com/alipay/agentUniverse
* gitee: https://gitee.com/agentUniverse/agentUniverse
* gitcode: https://gitcode.com/agentUniverse
* Stack Overflow: https://stackoverflowteams.com/c/agentuniverse/questions
* Discord: https://discord.gg/VfhEvJzQ
* 微信公众号: agentUniverse智多星
* 钉钉答疑群:
![](./docs/guidebook/_picture/dingtalk_util20250429.png)