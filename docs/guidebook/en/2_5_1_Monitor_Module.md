# Monitor Module

agentUniverse monitor module, mainly around the agent runtime LLM invocation/token expenses for data tracking and
recording. In this document, we will provide a detailed introduction on how to use the **LLM invocation tracking
capability** that is currently open in the agentUniverse.

## Monitor Configuration

Configure the monitor module settings in the main configuration file `config.toml` of agentUniverse, as follows:

```toml
[MONITOR]
activate = true
dir = './monitor'
```

- **`activate`**: The master switch for the monitor module is set to off by default. When set to true, it will turn on
  the LLM invocation tracking function of the agent runtime.
- **`dir`**: The local storage directory corresponding to the monitor module is, by default, the 'monitor' directory one
  level above the runtime directory. Users can customize the configuration of the directory path.

### LLM tracing configuration

For the LLM invocation tracking capability, agentUniverse also supports model granularity configuration. Once the main
switch of the monitor module is turned on, the invocation tracking function for specific models can be selectively
disabled through the LLM's yaml file.

For example, for a user-defined model such as `demo_llm`, if the tracing is set to false, then the invocation tracking
function for this model will be turned off.

```yaml
name: 'demo_llm'
description: 'demo openai'
model_name: 'gpt-4o'
max_tokens: 1000
max_retries: 2
tracing: false
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.default_openai_llm'
  class: 'DefaultOpenAILLM'
```

Special note: In the main configuration file of agentUniverse, the monitor module's master switch has the **highest
priority**. If the `activate` configuration is set to false, the model granularity configuration will not take effect.

## Monitor Module Introduction

### LLM Invocation Tracking

If the user utilizes the **default model class** supported by the agentUniverse, the feature can be used after the
configuration as described above is completed.

#### trace_llm Decorator

If a user customizes the extension based on the agentUniverse's model base class `LLM` to implement a custom model
invocation, it is necessary to add the `@trace_llm` decorator to the call/acall method of the custom model class.

Custom model example code as follows:

```python
from typing import Any, Iterator, Union, AsyncIterator

from agentuniverse.llm.llm import LLM, LLMOutput
from agentuniverse.base.annotation.trace import trace_llm


class DemoLLM(LLM):

    @trace_llm
    def call(self, messages: list, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        pass

    @trace_llm
    async def acall(self, *args: Any, **kwargs: Any) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        pass
```

agentUniverse implements the `@trace_llm` decorator, which, when the agent calls the corresponding LLM call/acall
methods, collects the model's prompt and response, serializes the information into JSON, and stores it in the local
storage directory corresponding to the monitor configuration in the form of a jsonl file, divided by the hour.

#### Demo Effect

Call the `demo_rag_agent` in the sample project of agentUniverse, using the gpt-4o model, with the query to analyze the
reasons behind Warren Buffett's reduction of his stake in BYD. The model invocation tracking function captures the
following data:

```json
{
  "source": "DefaultOpenAILLM.acall",
  "date": "2024-06-24 16:27:14",
  "llm_input": {
    "messages": [
      {
        "role": "system",
        "content": "You are an AI assistant proficient in information analysis.\nYour goal is to determine whether the corresponding answers to the questions provide valuable information, and to make suggestions and evaluations on the answers to the questions."
      },
      {
        "role": "user",
        "content": "The rules you need to follow are:\n1. You must answer the user's questions using English, combining the background information of the query with the knowledge you possess.\n2. Generate structured answers, and use blank lines to enhance the reading experience when necessary.\\n the question needs to be answered is: the reasons behind Warren Buffett's reduction of his stake in BYD\\n"
      }
    ]
  },
  "kwargs": {
    "model": "gpt-4o",
    "stream": false,
    "n": 1,
    "temperature": 0.5,
    "max_tokens": 1000
  },
  "llm_output": "Reasons Behind Warren Buffett's Reduction of His Stake in BYD\n\nWarren Buffett, through his company Berkshire Hathaway, has been reducing his stake in BYD since August 24, 2022. There are several potential reasons behind this decision:\n\n1. **Portfolio Rebalancing**:\n   - **Investment Strategy**: Buffett is known for his long-term investment strategy and value investing. Reducing his stake in BYD could be part of a broader portfolio rebalancing effort to diversify or allocate capital to other investment opportunities.\n   - **Profit Realization**: Given that Buffett's initial investment in BYD has appreciated significantly (approximately 31 times the initial value), selling some shares allows him to realize substantial profits.\n\n2. **Market Conditions**:\n   - **Stock Performance**: Despite the reduction in stake, BYD's stock price has remained relatively stable. This suggests that Buffett's decision to sell shares is not necessarily a reflection of a negative outlook on the company's stock performance.\n   - **Economic Factors**: The broader economic environment, including interest rates, inflation, and market volatility, may influence investment decisions. Buffett might be adjusting his holdings in response to these macroeconomic factors.\n\n3. **Company Evaluation**:\n   - **Intrinsic Value**: Buffett's investment philosophy focuses on the intrinsic value of a company rather than short-term stock price movements. He might believe that the current market price of BYD reflects its intrinsic value, prompting a partial exit.\n   - **Sector Analysis**: While BYD remains a leading player in the Chinese electric vehicle (EV) market, Buffett might be evaluating the competitive landscape and future growth prospects, leading to a strategic reduction in holdings.\n\n"
}
```

- **`source`**: the source of LLM invocation during agent runtime.
- **`date`**: LLM invocation time
- **`llm_input`**: LLM invocation messages and model parameters
- **`llm_output`**: LLM output text