# agentUniverse
****************************************
语言版本: [English](./README.md) | [中文](./README_zh.md) | [日本語](./README_jp.md)

![](https://img.shields.io/badge/framework-agentUniverse-pink)
![](https://img.shields.io/badge/python-3.10%2B-blue?logo=Python)
[![](https://img.shields.io/badge/%20license-Apache--2.0-yellow)](LICENSE)
[![Static Badge](https://img.shields.io/badge/pypi-v0.0.9-blue?logo=pypi)](https://pypi.org/project/agentUniverse/)

![](docs/guidebook/_picture/logo_bar.jpg)
****************************************

## agentUniverse是什么？

**agentUniverse 是一个基于大型语言模型的多智能体框架。** agentUniverse为您提供灵活易拓展的单智能体构建能力；agentUniverse核心拥有丰富的多智能体协同模式组件（可视为一个协同模式工厂Pattern Factory），它能让智能体们各司其职在解决不同领域问题时发挥最大的能力；同时agentUniverse专注于领域经验的融合，帮助您轻松将领域经验融入到智能体的工作中。🎉🎉🎉

**🌈🌈🌈agentUniverse帮助开发者、企业轻松构建出领域专家级别的强大智能体协同为您工作。**

![](docs/guidebook/_picture/agent_universe_framework_resize.jpg)

我们期待您通过社区对不同领域的Pattern进行实践与交流共享，框架也预置有若干已在真实产业中验证有效的多智能体协作模式组件，并在未来持续丰富。目前即将开放的模式组件包括：
* PEER 模式组件： 该pattern通过计划（Plan）、执行（Execute）、表达（Express）、评价（Review）四个不同职责的智能体，实现对复杂问题的多步拆解、分步执行，并基于评价反馈进行自主迭代，最终提升推理分析类任务表现。典型适用场景：事件解读、行业分析
* DOE 模式组件： 该pattern通过数据精制（Data-fining）、观点注入（Opinion-inject）、表达（Express）三个智能体，实现对数据密集、高计算精度、融合专家观点的生成任务的效果提升。典型适用场景：财报生成

更多模式组件持续推出中...

****************************************
## 目录
* [快速开始](#快速开始)
* [案例与样例工程](#案例与样例工程)
* [更多](#更多)
  * [为什么使用agentUniverse](#为什么使用agentUniverse)
  * [核心特性](#核心特性)
  * [用户指南](#用户指南)
  * [API参考](#API参考)
  * [支持](#支持)
  * [鸣谢](#鸣谢)
****************************************
## 快速开始
使用pip：
```shell
pip install agentUniverse
```

我们将向您展示如何：
* 进行环境与应用工程准备
* 构建一个简单的agent
* 使用模式组件完成多agent协同
* 对agent执行效果进行测试调优
* 对agent进行快速服务化

详情请阅读[快速开始](docs/guidebook/zh/1_3_%E5%BF%AB%E9%80%9F%E5%BC%80%E5%A7%8B.md) 。
****************************************
## 案例与样例工程
### 🌟 使用案例
[法律咨询Agent](./docs/guidebook/zh/7_1_1_法律咨询案例.md)

[Python代码生成与执行Agent](./docs/guidebook/zh/7_1_1_Python自动执行案例.md)

[基于多轮多Agent的讨论小组](./docs/guidebook/zh/6_2_1_讨论组.md)

### 🌟 示例项目
[agentUniverse 示例项目](sample_standard_app)

### 🌟 使用aU构建的产品案例
[支小助 金融从业专家AI助手](https://zhu.alipay.com/)
****************************************
## 更多
### 为什么使用agentUniverse
💡 [为什么使用agentUniverse?](./docs/guidebook/zh/1_为什么选择agentUniverse.md)

### 核心特性

* **丰富的多智能体协同模式：** 提供PEER（Plan/Execute/Express/Review）、DOE（Data-fining/Opinion-inject/Express）等产业中验证有效的协同模式，同时支持用户自定义编排新模式，让多个智能体有机合作；

* **所有组件均可定制：** LLM、知识、工具、记忆等所有框架组件均提供自定义能力，供用户来增强专属智能体；

* **轻松融入领域经验：** 提供领域prompt、知识构建与管理的能力，同时支持领域级SOP编排与注入，将智能体对齐至领域专家级别；

💡 更多特定见[agentUniverse核心特性](docs/guidebook/zh/1_核心特性.md)部分。

### 用户指南
💡 更多详细信息，请阅读[用户指南](docs/guidebook/zh/0_%E7%9B%AE%E5%BD%95.md) 。

### API参考
💡 请阅读[readthedocs](https://agentuniverse.readthedocs.io/en/latest/) 。

### 支持
#### 通过github issue提交疑问
😊 我们建议您使用[github issue](https://github.com/alipay/agentUniverse/issues) 提交您的疑问, 我们通常会在2日内回复。

#### 通过Discord联系我们
😊 加入我们的 [Discord频道](https://discord.gg/DHFcdkWAhn) 与我们进行交流。

#### 通过钉钉群联系我们
😊 加入我们的钉钉答疑群与我们联系。
![](./docs/guidebook/_picture/dingtalk_util20250429.png)

#### 通过管理员Email联系我们
😊 Email: [jerry.zzw@antgroup.com](mailto:jerry.zzw@antgroup.com)

#### 微信公众号

😊 公众号ID：**agentUniverse智多星**

更多相关的文章与资讯你可以在微信公众号中获取。

## 鸣谢
本项目部分基于langchain、pydantic、gunicorn、flask、SQLAlchemy、chromadb等（详细依赖列表可见pyproject.toml）优秀开源项目实现，在此特别感谢相关项目与关联方。 🙏🙏🙏
