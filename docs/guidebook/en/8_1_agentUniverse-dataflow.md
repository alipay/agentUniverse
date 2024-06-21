# Project Introduction
agentUniverse-dataflow is the project based on the idea of **Agentic Workflow**, utilizing the multi-agent and flow orchestration approach. It enhances the data processing workflow of LLM and agents through **offline adaptive LLM data collection, fine-tuning dataset generation, model inference training, and multi-dimensional automatic dataset evaluation, etc.**

Including:
1. A foundational data framework: **DataFramework**, structured around the Dispatch-Flow-Node-Data/Event/Prompt/Answer/Eval, with capabilities for sustainable integration and expansion.
2. An agent framework: **PVRP** (Planner-Verifier-Reflector-Producer).
3. A set of capabilities:
   - Adaptive data event collection: **auto_event**
   - Fine-tuning dataset generation: **dataset_build**
   - Uploading for training and inference: **train_dump**
   - Multi-dimensional objective automatic evaluation: **eval_report**
   - Model deployment and activation: **model_deploy**
   - System instruction optimization: **instruct_select**

# Quick Start
In the agentUniverse standard project template `sample_standard_app`:
## step1
Configure the loading path of prompt in config.toml, add `agentuniverse_dataflow.prompt`, and read the built-in prompt files of agentuniverse_dataflow.
```toml
[CORE_PACKAGE]
# Perform a full component scan and registration for all the paths under this list.
default = ['sample_standard_app.app.core']
# Scan and register agent components for all paths under this list, with priority over the default.
agent = ['sample_standard_app.app.core.agent']
# Scan and register agent components for all paths under this list, with priority over the default.
knowledge = ['sample_standard_app.app.core.knowledge']
# Scan and register knowledge components for all paths under this list, with priority over the default.
llm = ['sample_standard_app.app.core.llm']
# Scan and register llm components for all paths under this list, with priority over the default.
planner = ['sample_standard_app.app.core.planner']
# Scan and register planner components for all paths under this list, with priority over the default.
tool = ['sample_standard_app.app.core.tool']
# Scan and register memory components for all paths under this list, with priority over the default.
memory = ['sample_standard_app.app.core.memory']
# Scan and register service components for all paths under this list, with priority over the default.
service = ['sample_standard_app.app.core.service']
# Scan and register prompt components for all paths under this list, with priority over the default.
prompt = ['sample_standard_app.app.core.prompt', 'agentuniverse_dataflow.prompt']
```
## step2
Under the dataflow directory of sample_standard_app, dispatch is used as the entry, configure the dataflow process in `dispatch.yaml`, and then run the `dispatch.py` file (the results of the dataflow run are stored in the dispatch/data directory as jsonl).

![picture](../_picture/dataflow_dispatch.png) 

In the `dispatch.yaml` file, users can customize and edit the dataflow task nodes that need to be run, such as the following configuration file. After dataflow runs, it performs two tasks: **adaptive data event collection and fine-tuning dataset generation**.
```yaml
name: 'main_dispatch'
description: 'dispatch with multi-dataflows which will execute one after another'
dataflows:
  - ../flow/auto_event.yaml
  - ../flow/dataset_build.yaml
```

# Dataflow Introduction
agentUniverse-dataflow currently supports six kinds of flow, namely `auto_event/dataset_build/train_dump/eval_report/model_deploy/instruct_select`, and each flow is combined through nodes to form a corresponding pipeline.
## Dataflow Flowchart
![picture](../_picture/dataflow_flowchart.jpg) 

In the yaml configuration file of each flow, each node contains llm and prompt version configuration information. **Users can customize the llm and prompt to achieve version management and quick switching.** 
For example, the node in the following figure uses the QWen model of the sample project and the built-in prompt file of agentuniverse_dataflow:

![picture](../_picture/dataflow_dataset_build.png)  
## Flow Detailed Introduction
**Special instruction:** 
`Auto event/dataset build/eval report/instruct select` in dataflow is a flow node that **users can directly run and experience**. The `train dump and model deploy` node mainly **provide the flow concept**. At present, they have been deployed and run through the standard model and training platform in Ant Group, and the open source community version will consider opening up later.
### Auto Event
The main function of Auto Event is to collect different data sources, perceive the log information of the corresponding agent runtime in the data source, extract valid input and output to generate specific jsonl files (currently the collection of jsonl data source is supported, and more data source types remain open.

Auto Event contains three nodes, `Perceiver/Planner/Executor`, configured through yaml, and the example configuration file is `auto_event.yaml` in sample_standard_app. 
 - Perceiver Node: perceive the data source and extracting the original input and output from the data source.
 - Planner Node: generate code to extract valid model input and output from the data source. 
 - Executor Node: execute code to extract valid model input and output from the data source.

### Dataset Build
The main function of Dataset Build is to generate domain-specific high-quality q&a datasets.

Dataset Build contains six nodes, `Seed/Rewrite/Extend/Dedupe/Answer/Filter`, configured through yaml, and the example configuration file is `dataset_build.yaml` in sample_standard_app.
 - Seed Node: user-specified domain to produce rough query sets.
 - Rewrite Node: rewrite rough query sets to standard query sets.
 - Extend Node: extent query sets.
 - Dedupe Node: de-duplicate query sets.
 - Answer Node: LLM calls the query sets to generate the q&a datasets.
 - Filter Node: professional domain evaluation criteria to filter valid datasets.

### Train Dump
The main function of Train Dump is to upload specified data sets, sft training model, and dump q&a result sets.

Train Dump contains four nodes, `Upload/Train/PreDeploy/Dump`, configured through yaml, and the example configuration file is `train_dump.yaml` in sample_standard_app.
 - Upload Node: upload datasets to the model training platform.
 - Train Node: train model according to fine-tuning data sets.
 - PreDeploy Node: pre-deploy the model after training.
 - Dump Node: dump q&a result sets according to query sets.

### Eval Report
The main function of Eval Report is to evaluate the quality of q&a result sets and generate evaluation reports.

Eval Report contains two nodes, `Eval/Report`, configured through yaml, and the example configuration file is `eval_report.yaml` in sample_standard_app.
 - Eval Node: multidimensional evaluation of the quality of q&a result sets.
 - Report Node: generate quality assessment reports.

### Model Deploy
The main function of Model Deploy is to formally deploy the post-training model, dump q&a result sets.

Model Deploy contains two nodes, `Deploy/Dump`, configured through yaml, and the example configuration file is `model_deploy.yaml` in sample_standard_app.
 - Deploy Node: formal deployment of the trained model.
 - Dump Node: dump q&a result sets according to query sets.

### Instruct Select
The main function of Instruct Select is to generate instruction sets, assemble complete prompt sets, dump q&a result sets, and evaluate the quality of result sets.

Instruct Select contains four nodes, `Seed/PromptGen/Dump/Eval`, configured through yaml, and the example configuration file is `instruct_select.yaml` in sample_standard_app.
 - Seed Node: generate instruction sets based on user-specified domain.
 - PromptGen Node: merge instruction sets and query sets into complete prompt sets.
 - Dump Node: dump q&a result sets according to query sets.
 - Eval Node: multi-dimensional evaluation of the quality of q&a result sets.