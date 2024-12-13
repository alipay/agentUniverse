# 文档说明
为了让大家快速上手AU框架，我们提供了样板工程（可以直接运行）并配套详细的文字说明，在实际研发过程中直接基于其中的某些智能体结合自己业务进行一小部分代码/配置改写即可完成应用的搭建。

样板工程地址：[au_sample_standard_app](../../../../demo_startup_app)

样板工程拟定了业务是关于宠物险产品的智能顾问，对用户提出的产品问题进行解答。

# 从一个智能体搭建开始
[single_agent_case](../../../../demo_startup_app/intelligence/agentic/agent/agent_instance/single_agent_case)下构建一个宠物险顾问智能体，使用qwen72b模型，提供宠物医保的检索以及信息补充工具，react模式自行让模型选择工具帮助回答用户的问题。

从0开始搭建的整体流程如下：

![画板](https://intranetproxy.alipay.com/skylark/lark/0/2024/jpeg/18056974/1733987419009-14ac52dc-dc1b-4998-a7ff-fc2176083720.jpeg)

## 构建agent所依赖的组件
### 构建tool
**<配置封装>**
[pet_insurance_search_context_tool.yaml](../../../../demo_startup_app/intelligence/agentic/tool/pet_ins/pet_insurance_search_context_tool.yaml)

![](https://intranetproxy.alipay.com/skylark/lark/0/2024/png/18056974/1733990583392-c4df1a8b-51d1-44a9-84e9-ebf7c4251c0b.png)

**<代码实现>**
[pet_insurance_search_context_tool.py](../../../../demo_startup_app/intelligence/agentic/tool/pet_ins/pet_insurance_search_context_tool.py)

所有的自定义工具都都继承自agentuniverse.agent.action.tool.tool的Tool基类，核心执行方法为execute（你需要overwrite的地方），入参类型为ToolInput（key-value经过封装后的结构）。

![](https://intranetproxy.alipay.com/skylark/lark/0/2024/png/18056974/1733988837626-fd96612d-6439-4aa0-841a-916031b51bdf.png)

API适配AU样例可参考 [API适配样例文档.md](API适配样例文档.md)

### 构建llm
#### 配置封装
[pet_qwen_72b_stream.yaml](../../../../demo_startup_app/intelligence/agentic/llm/maya/pet_qwen_72b_stream.yaml)
拓展字段ext_info中可以添加自定义参数，并在代码初始化方法中解析，成为PetInsuranceMayaLLM的属性。

#### 代码实现
所有的llm都继承自agentuniverse.llm.llm的LLM基类。

**初始化**

![](https://intranetproxy.alipay.com/skylark/lark/0/2024/png/18056974/1733990996692-856663e2-1618-4d5a-b837-0cbdaac6e092.png)

overwrite方法initialize_by_component_configer，基于父类的方法，在ext_info中添加一些自定义参数。如llm走的是企业内部maya服务，需要sceneName，chainName等参数，在初始化中注入之后就可以通过在yaml中配置生效。

**执行主体逻辑**

![](https://intranetproxy.alipay.com/skylark/lark/0/2024/png/18056974/1733998236348-4ab62c1e-c05b-4e24-b0c9-f306a6eecb3b.png)

llm需要封装成langchain实例，实际调度过程中由该实例唤起执行call方法。call方法为主体逻辑，在样例中对流式和非流式分别实现了http的模型请求调用。

注意：样例所用的llm为

## 构建智能体
#### 配置封装
[pet_insurance_react_agent.yaml](../../../../demo_startup_app/intelligence/agentic/agent/agent_instance/single_agent_case/pet_insurance_react_agent.yaml)

![](https://intranetproxy.alipay.com/skylark/lark/0/2024/png/18056974/1734003384746-701f2ff8-46b7-4d32-9cdb-0bb7594594b1.png)

该智能体依赖的prompt定义 [pet_insurance_react_prompt.yaml](../../../../demo_startup_app/intelligence/agentic/prompt/pet_react_agent/pet_insurance_react_prompt.yaml)


![](https://intranetproxy.alipay.com/skylark/lark/0/2024/png/18056974/1734071728918-f8608995-b782-4fdd-9374-072845c839d7.png)

react模式完全依赖llm自行思考问题，选择工具调度组装结果，在实际使用过程中需要注意思维链的迭代，尤其是停止词stop的配置（一般为Observation），不同模型对prompt需要进行微调去适配。

#### 代码实现
![](https://intranetproxy.alipay.com/skylark/lark/0/2024/png/18056974/1733985532204-5f738d83-7163-4b1e-a948-cd413699c579.png)

智能体继承Agent类，框架会对input_keys进行校验，一定要注意输入和输出字段。

上图示例是一个react智能体，执行主体execute方法中依次对memory，token，llm，tool加工处理后基于langchain构建了reAct实例，该实例通过invoke方法唤起。

## 运行测试
![](https://intranetproxy.alipay.com/skylark/lark/0/2024/png/18056974/1734001509704-bd0c67c8-e98e-44f3-8c36-a2a78bce2b09.png)

![](https://intranetproxy.alipay.com/skylark/lark/0/2024/png/18056974/1734001585855-35f64dd1-1af1-4e79-bcbc-f30b836f0a21.png)

能看到这个思维链是先去调用pet_insurance_info_tool来获取“宠物医保”的详细信息，再去使用pet_insurance_search_context_tool尝试找到关于升级流程的直接信息。

最终的回答为: “宠物医保”在保障期间内不支持升级或更改版本。如果您希望获得更高一级的保障，您需要在当前保险周期结束时，在续保时选择您想要的更高保障版本。例如，如果您目前投保的是基础版，那么在保险到期后，您可以选择续保时升级到升级版或尊享版。请记得在续保时仔细阅读条款，以确保您了解新版本的所有细节和费用。

## 效果微调-优化prompt
优化prompt是调整智能体效果的常用手段。2.3中运行结果的表达相对啰嗦和重复，希望在表达上能够更精简，我们可以适当修改pet_insurance_react_agent.cn，优化llm的结果输出。

![](https://intranetproxy.alipay.com/skylark/lark/0/2024/png/18056974/1734072545230-55d74f48-f555-4beb-9087-a4d4b5f031a2.png)

运行后的效果如下，对比2.3要好些。

![](https://intranetproxy.alipay.com/skylark/lark/0/2024/png/18056974/1734072518223-8d7966d4-cd3c-4268-8395-e572f1ae5432.png)

## 服务化
[pet_insurance_react_service.yaml](../../../../demo_startup_app/intelligence/service/agent_service/pet_insurance_react_service.yaml)

![](https://intranetproxy.alipay.com/skylark/lark/0/2024/png/18056974/1734005968227-3039b182-09e2-49d2-982b-60e3df1e265e.png)

本地起服务调试，构建下面的请求

![](https://intranetproxy.alipay.com/skylark/lark/0/2024/png/18056974/1734005989173-7b555ca3-614e-4717-baa9-2012e6a9c57a.png)

# 从单智能体到多智能体
对于比较复杂的场景，单智能可能不足以完成任何，需要多个智能体协作。

以样板工程的宠物险问答为例，由于用户的问题可能比较发散，单智能体的回答有时候会产生偏离。在部分专家经验的驱动下，对于这种场景我们拆分以下几个智能体。

![画板](https://intranetproxy.alipay.com/skylark/lark/0/2024/jpeg/18056974/1734014243591-e9539d7d-4bb6-45c0-95f3-698093449058.jpeg)

## 子智能体
改写和策划两个子智能体不再单独介绍了，参考2.1进行构建

改写智能体：
[pet_question_rewrite_agent.yaml](../../../../demo_startup_app/intelligence/agentic/agent/agent_instance/multi_agent_case/pet_question_rewrite_agent.yaml)


策划智能体（拆解问题）：
[pet_question_planning_agent.yaml](../../../../demo_startup_app/intelligence/agentic/agent/agent_instance/multi_agent_case/pet_question_planning_agent.yaml)


这里要注意的是出入参的定义和转换，要能和下个智能体衔接起来。这个可以在主智能体串接时适配。

![](https://intranetproxy.alipay.com/skylark/lark/0/2024/png/18056974/1734014843998-a826cd8b-3d4f-4fb4-9ef0-65e622983368.png)

## 主智能体
[pet_insurance_consult_agent.yaml](../../../../demo_startup_app/intelligence/agentic/agent/agent_instance/multi_agent_case/pet_insurance_consult_agent.yaml)

![](https://intranetproxy.alipay.com/skylark/lark/0/2024/png/18056974/1734014662057-cbd2eae4-8d92-4a28-8717-fa42bf6229c0.png)

实际上就是把几个智能体和工具按照一定的逻辑串接起来，这里要注意的是参数的传递，agent_input作为线程上下文可以存储中间产物给后面的智能体使用，每个智能体的出入参字段是可以按照需求自定义，建议不要重复。

## 运行测试

运行 [pet_insurance_consult_pro_agent_test.py](../../../../demo_startup_app/intelligence/test/pet_insurance_consult_pro_agent_test.py)


![](https://intranetproxy.alipay.com/skylark/lark/0/2024/png/18056974/1734073361810-67db902b-4ede-4bbf-bd4d-c9f937434536.png)

**智能体 pet_question_planning_agent 执行结果为： **

```text
如何将宠物医保的基础版升级到升级版或尊享版？升级的具体流程和条件是什么？
```

**智能体 pet_question_planning_agent 执行结果为：**

```json
 {
    "sub_query_list": [
        "如何将宠物医保的基础版升级到升级版或尊享版？",
        "宠物医保升级版和尊享版的具体保障内容有什么区别？",
        "升级宠物医保版本是否需要额外费用，费用如何计算？"
    ]
}
```

**pet_insurance_consult_agent 最终执行结果：**

```text
宠物医保在保障期间内不支持从基础版升级到升级版或尊享版。您如果希望获得更高版本的保障，可以在当前保单到期后，在续保时选择升级到所需的版本。
请注意，续保时的保费可能会根据宠物的当前状况和保险公司的评估有所调整。
```



# 封装智能体模版
在上面的多智能体应用中我们会发现，三个智能体在实现上有很多相同的逻辑，甚至策划智能体继承自改写智能体。为了提升智能体的复用性，我们可以抽像出一些通用的逻辑和方法，封装成一个智能体模版AgentTemplate，大部分智能体基于这个模版做一些微小的调整，甚至只是yaml配置的改动即可实现多种智能体逻辑。

参考 [pet_agent_template.py](../../../../demo_startup_app/intelligence/agentic/agent/agent_template/pet_agent_template.py)

![](https://intranetproxy.alipay.com/skylark/lark/0/2024/png/18056974/1734016162848-dc15f8cf-c362-4834-b99b-abe9e0ba2cdc.png)

这里将智能体会用到的包括注册agent，处理记忆/llm/工具/prompt以及执行主体的一些通用方法进行了一定的抽象，这些方法在宠物险的智能体中大部分都可以复用。以主智能体为例，只要overwrite方法customized_execute对主流程部分逻辑进行定制化即可。

![](https://intranetproxy.alipay.com/skylark/lark/0/2024/png/18056974/1734016447429-99561e21-98fa-45f2-8e55-8a9a696f8022.png)

实际上AU框架提供了相当多的智能体模版，包括Rag，React，PEER模式等，建议使用这些现有的模版构建自己的智能体。

![](https://intranetproxy.alipay.com/skylark/lark/0/2024/png/18056974/1734016549408-58b1b46e-6f09-4339-b819-7efccab3d78b.png)

