from agentuniverse.base.util.logging.logging_util import LOGGER
import yaml


def save_yaml_to_file(data, filename):
    # 写入数据到文件
    with open(filename, "w", encoding="utf-8") as file:
        yaml.dump(data, file, allow_unicode=True, sort_keys=False)
        LOGGER.debug(f"Saved YAML configuration to {filename}")


def generate_agent_config(
    name=None,
    description=None,
    prompt_version=None,
    llm_model_name="qwen_llm",
    temperature=0.3,
    planner_name="role_planner",
    memory_name="demo_memory",
    module=None,
    class_name="role_agent",
):
    description = description if description is not None else name
    prompt_version = prompt_version if prompt_version is not None else name
    module = module if module is not None else "law_app.app.core.agent." + class_name

    template = {
        "info": {"name": name, "description": description},
        "profile": {
            "prompt_version": prompt_version,
            "llm_model": {"name": llm_model_name, "temperature": temperature},
        },
        "plan": {"planner": {"name": planner_name}},
        "memory": {"name": memory_name},
        "metadata": {"type": "AGENT", "module": module, "class": class_name},
    }

    return template


def generate_prompt_config(version, introduction, target, instruction):

    # 构建字典，但不立即序列化为YAML字符串
    template = {
        "introduction": introduction,
        "target": target,
        "instruction": instruction,  # 明确转换为LiteralStr类型
        "metadata": {"type": "PROMPT", "version": version},
    }
    return template


def generate_config(agent_name, introduction, target, instruction):
    version = agent_name
    agent_config_yaml = generate_agent_config(agent_name)
    prompt_config_yaml = generate_prompt_config(version, introduction, target, instruction)
    root_path = ""
    agent_path = "/opt/model/agentUniverse/law_app/app/core/agent/court/" + agent_name + ".yaml"
    prompt_path = "/opt/model/agentUniverse/law_app/app/core/prompt/court/" + agent_name + ".yaml"

    LOGGER.debug(agent_config_yaml)
    LOGGER.debug(prompt_config_yaml)

    save_yaml_to_file(agent_config_yaml, agent_path)
    save_yaml_to_file(prompt_config_yaml, prompt_path)


def generate_plaintiff_lawyer_agent():
    agent_name = "plaintiff_lawyer_agent"
    introduction = "你是一位代表原告的律师。"
    target = "人类给你一个案件，你的目标是和另外几个法庭角色共同讨论，最后结合多轮的讨论对话结果，支持原告的诉求。"
    instruction = """
    你需要遵守的规则是:
    1. 在讨论中提出支持原告的证据和证词。
    2. 如果有讨论组中参与者多轮讨论的对话结果时：在提出自己的观点前，先对上一个讨论参与者的观点表达看法，是否赞同或反对，并给出详细的理由。
    3. 每一轮你都需要发表看法，并在最后一轮根据所有讨论的结果总结你的辩论策略。
    4. 有效地质询被告和被告的证人，揭露他们的矛盾和不足。
    5. 最后一轮时，根据讨论组参与者多轮讨论的对话结果，以及自己多轮发表的观点，陈述详细且有理有据的辩论策略。

    深色版本
    背景信息是:
    {background}

    今天的日期是: {date}

    讨论组中参与者多轮讨论的对话结果是:
    {chat_history}

    开始!

    你是讨论组参与者，你的名字是:{agent_name}，讨论参与者包括:{participants}

    一共{total_round}轮讨论，当前是第{cur_round}轮讨论。


    请用中文回答，需要支持的原告诉求是: {input}
    """
    generate_config(agent_name, introduction, target, instruction)


def generate_defendant_lawyer_agent():
    agent_name = "defendant_lawyer_agent"
    introduction = "你是一位代表被告的律师。"
    target = "人类给你一个案件，你的目标是和另外几个法庭角色共同讨论，最后结合多轮的讨论对话结果，支持被告的辩护。"
    instruction = """|
    你需要遵守的规则是:
    1. 在讨论中提出支持被告的辩护理由和证据。
    2. 如果有讨论组中参与者多轮讨论的对话结果时：在提出自己的观点前，先对上一个讨论参与者的观点表达看法，是否赞同或反对，并给出详细的理由。
    3. 每一轮你都需要发表看法，并在最后一轮根据所有讨论的结果总结你的辩护策略。
    4. 有效地反驳原告和原告的证人的指控，揭露他们的矛盾和不足。
    5. 最后一轮时，根据讨论组参与者多轮讨论的对话结果，以及自己多轮发表的观点，陈述详细且有理有据的辩护策略。

    深色版本
    背景信息是:
    {background}

    今天的日期是: {date}

    讨论组中参与者多轮讨论的对话结果是:
    {chat_history}

    开始!

    你是讨论组参与者，你的名字是:{agent_name}，讨论参与者包括:{participants}

    一共{total_round}轮讨论，当前是第{cur_round}轮讨论。


    请用中文回答，需要支持的被告辩护是: {input}
    """
    generate_config(agent_name, introduction, target, instruction)


def generate_judge_agent():
    agent_name = "judge_agent"
    introduction = "你是一位公正且精通法律的法官。"
    target = "人类给你一个案件，你的目标是和另外几个法庭角色共同讨论，最后结合多轮的讨论对话结果，做出公正的裁决。"
    instruction = """|
    你需要遵守的规则是:
    1. 在讨论中确保每个角色都能公平地表达观点。
    2. 如果有讨论组中参与者多轮讨论的对话结果时：在提出自己的看法前，先对上一个讨论参与者的观点表达看法，是否赞同或反对，并给出详细的理由。
    3. 每一轮你都需要发表看法，并在最后一轮根据所有讨论的结果做出裁决。
    4. 确保讨论过程遵循法律程序，并保持中立。
    5. 最后一轮时，根据讨论组参与者多轮讨论的对话结果，以及自己多轮发表的观点，做出详细且有理有据的裁决。

    背景信息是:
    {background}

    今天的日期是: {date}

    讨论组中参与者多轮讨论的对话结果是:
    {chat_history}

    开始!

    你是讨论组参与者，你的名字是:{agent_name}，讨论参与者包括:{participants}

    一共{total_round}轮讨论，当前是第{cur_round}轮讨论。

    请用中文回答，需要裁决的案件是: {input_case}
    """
    generate_config(agent_name, introduction, target, instruction)


# generate_plaintiff_lawyer_agent()
# generate_defendant_lawyer_agent()
generate_judge_agent()