# agentUniverse
****************************************
Language version: [English](./README.md) | [中文](./README_zh.md) | [日本語](./README_jp.md)

![](https://img.shields.io/badge/framework-agentUniverse-pink)
![](https://img.shields.io/badge/python-3.10%2B-blue?logo=Python)
[![](https://img.shields.io/badge/%20license-Apache--2.0-yellow)](LICENSE)
[![Static Badge](https://img.shields.io/badge/pypi-v0.0.9-blue?logo=pypi)](https://pypi.org/project/agentUniverse/)

![](docs/guidebook/_picture/logo_bar.jpg)
****************************************

## What is agentUniverse?

**agentUniverse is a multi-agent framework based on large language models.** agentUniverse provides you with the flexible and easily extensible capability to build single agents. At its core, agentUniverse features a rich set of multi-agent collaboration mode components (which can be viewed as a Collaboration Mode Factory, or Pattern Factory). These components allow agents to maximize their effectiveness by specializing in different domains to solve problems. agentUniverse also focuses on the integration of domain expertise, helping you seamlessly incorporate domain knowledge into the work of your agents.🎉🎉🎉

**🌈🌈🌈agentUniverse helps developers and enterprises to easily build powerful collaborative agents that perform at an expert level in their respective domains.**

![](docs/guidebook/_picture/agent_universe_framework_resize.jpg)

We encourage you to practice and share different domain Patterns within the community. The framework comes pre-loaded with several multi-agent collaboration mode components that have been validated in real-world industries and will continue to expand in the future. The components that will be available soon include:

* PEER Mode Component: This pattern uses agents with different responsibilities—Plan, Execute, Express, and Review—to break down complex problems into manageable steps, execute the steps in sequence, and iteratively improve based on feedback, enhancing the performance of reasoning and analysis tasks. Typical use cases: Event interpretation, industry analysis.
* DOE Mode Component: This pattern employs three agents—Data-fining, Opinion-inject, and Express—to improve the effectiveness of tasks that are data-intensive, require high computational precision, and incorporate expert opinions. Typical use cases: Financial report generation.

More patterns are coming soon...

****************************************
## Table of Contents
* [Quick Start](#Quick Start)
* [Cases and Example Projects](#Cases and Example Projects)
* [More](#More)
  * [Why Use agentUniverse](#Why Use agentUniverse)
  * [Core Features](#Core Features)
  * [User Guide](#User Guide)
  * [API Reference](#API Reference)
  * [Support](#Support)
  * [Acknowledgements](#Acknowledgements)
****************************************
## Quick Start
Using pip:
```shell
pip install agentUniverse
```

We will show you how to:

* Prepare the environment and application projects
* Build a simple agent
* Use mode components for multi-agent collaboration
* Test and tune the execution effectiveness of an agent
* Quickly deploy an agent as a service

For more details, please read the [Quick Start](./docs/guidebook/en/1_3_Quick_Start.md).

****************************************
## Cases and Example Projects
### 🌟 Use Cases
[Legal Consultation Agent](./docs/guidebook/en/7_1_1_Legal_Consultation_Case.md)
[Python Code Generation and Execution Agent](./docs/guidebook/en/7_1_1_Python_Auto_Runner.md)
[Discussion Group Based on Multi-Turn Multi-Agent Mode](./docs/guidebook/en/6_2_1_Discussion_Group.md)  
[Financial Event Analysis Based on PEER Multi-Agent Mode](./docs/guidebook/en/6_4_1_Financial_Event_Analysis_Case.md)

### 🌟 Example Projects
[agentUniverse Example Projects](sample_standard_app)

### 🌟 Product Cases Built with agentUniverse
['Zhi Xiao Zhu' AI Assistant for Financial Professionals](https://zhu.alipay.com/)
****************************************
## More
### Why Use agentUniverse
💡 [Why Use agentUniverse?](./docs/guidebook/en/1_Why_Use_agentUniverse.md)

### Core Features

* **Rich Multi-Agent Collaboration Modes:** Provides industry-validated collaboration modes such as PEER (Plan/Execute/Express/Review) and DOE (Data-fining/Opinion-inject/Express). It also supports user-defined patterns for new modes, enabling organic collaboration among multiple agents.
* **Customizable Components:** All framework components, including LLM, knowledge, tools, and memory, are customizable, allowing users to enhance their dedicated agents.
* **Seamless Integration of Domain Expertise:** Offers capabilities for domain-specific prompts, knowledge construction, and management, and supports domain-level SOP orchestration and embedding, aligning agents to the expert level in their fields.

💡 For more specific details, see the [Core Features of agentUniverse](./docs/guidebook/en/1_Core_Features.md).

### User Guide
💡 For more detailed information, please read the [User Guide](./docs/guidebook/en/0_index.md).

### API Reference
💡 Please read the [API Reference](https://agentuniverse.readthedocs.io/en/latest/).

### Support
#### Submit Questions via GitHub Issues
😊 We recommend submitting your queries using [GitHub Issues](https://github.com/alipay/agentUniverse/issues), we typically respond within 2 days.

#### Contact Us via Discord
😊 Join our [Discord Channel](https://discord.gg/VfhEvJzQ) to interact with us.

#### Contact Us via DingTalk
😊 Join our DingTalk support group to get in touch with us.
![](./docs/guidebook/_picture/dingtalk_util20250429.png)

#### Contact Us via Administrator Email
😊 Email: [jerry.zzw@antgroup.com](mailto:jerry.zzw@antgroup.com)

#### WeChat Official Account

😊 Official Account ID: **agentUniverse智多星** 

You can get more related articles and information in our WeChat Official Account.

## Acknowledgements
This project is partially built on excellent open-source projects such as langchain, pydantic, gunicorn, flask, SQLAlchemy, chromadb, etc. (The detailed dependency list can be found in pyproject.toml). We would like to extend special thanks to the related projects and contributors. 🙏🙏🙏
