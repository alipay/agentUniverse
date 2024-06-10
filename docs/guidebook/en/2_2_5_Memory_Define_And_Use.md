# How to Define the Memory Component
The current version of the agentUniverse memory component includes default memory capabilities, and we are in the process of upgrading it. Therefore, we will not detail this part for now. If you are interested in the current memory design, you can refer to the `agentuniverse.agent.memory.memory.Memory` object. In future versions, we will enable the ability to customize memory, and we will update this part of the documentation accordingly.

# How to Use the Memory Component
## Configuring Memory in the Agent
Following the [Creating and Using Agents](2_2_1_Agent_Create_And_Use.md) guide, you can set up your memory instance in the agent's memory section. The current version of aU includes a default memory type, which you can configure as follows:
```yaml
info:
  name: 'demo_rag_agent'
  description: 'demo rag agent'
profile:
  introduction: You are an AI assistant skilled in information analysis.
  target: Your goal is to assess whether the answers to questions provide valuable information and to give recommendations and evaluations on the answers.
  instruction: |
    The rules you need to abide by are:
    1. Always answer users' questions in Chinese, combining it with the background information you have.
    2. Structure the answers well and use blank lines to enhance readability when necessary.
    3. Do not use incorrect information from the background.
    4. Consider the relevance of the answer to the question and avoid unhelpful responses.
    5. Provide thorough answers, highlight the key points, and avoid excessive verbosity.
    6. Avoid vague speculation.
    7. Use numerical information as much as possible.
    Background information is:
    {background}
  
    Previous conversation:
    {chat_history}
    
    Let's begin!
    The question to answer is: {input}
  llm_model:
    name: 'demo_llm'
    model_name: 'gpt-4o'
plan:
  planner:
    name: 'rag_planner'
action:
  tool:
    - 'google_search_tool'
memory:
  name: 'default_memory'
metadata:
  type: 'AGENT'
  module: 'sample_standard_app.app.core.agent.rag_agent_case.demo_rag_agent'
  class: 'DemoRagAgent'
```

Currently, agentUniverse only provides the default_memory type. This memory type will retrieve the chat_history keyword from the conversation, and automatically summarize the memory when its length exceeds a certain threshold.

## Passing chat_history when Calling the Agent
When invoking the agent, you can pass the chat_history parameter, such as:

```text
chat_history=[{"content": "Hello", "type": "human"}, {"content": "Hello", "type": "ai"}]
```

The default_memory instance will retrieve this parameter during agent execution and process the memory accordingly throughout the agent's execution process.

## Using the Memory Manager
You can get the Memory instance corresponding to its name using the `.get_instance_obj(xx_memory_name)` method in the Memory Manager.

```python
from agentuniverse.agent.memory.memory_manager import MemoryManager

memory = MemoryManager().get_instance_obj(component_instance_name=memory_name, new_instance=True)
```

# Conclusion
Now you have mastered the method of using the Memory component. Go ahead and try using Memory.