#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time   : 2024/7/22 11:51
# @Author : fluchw
# @Email  : zerozed00@qq.com
# @File   ：game_part_1_planner.py
import asyncio

from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory

from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.agent_model import AgentModel
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.chat_memory import ChatMemory
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.plan.planner.planner import Planner
from agentuniverse.base.util.logging.logging_util import LOGGER
from agentuniverse.base.util.memory_util import generate_memories
from agentuniverse.base.util.prompt_util import process_llm_token
from agentuniverse.llm.llm import LLM
from agentuniverse.prompt.chat_prompt import ChatPrompt
from agentuniverse.prompt.prompt import Prompt
from agentuniverse.prompt.prompt_manager import PromptManager
from agentuniverse.prompt.prompt_model import AgentPromptModel

default_round = 1


class game_part_1_planner(Planner):
    """Discussion planner class."""

    # current_round = 0

    def invoke(self, agent_model: AgentModel, planner_input: dict, input_object: InputObject) -> dict:
        """Invoke the planner.

        Args:
            agent_model (AgentModel): Agent model object.
            planner_input (dict): Planner input object.
            input_object (InputObject): The input parameters passed by the user.
        Returns:
            dict: The planner result.
        """
        planner_config = agent_model.plan.get('planner')
        # generate role agents
        role_agents = self.generate_role_agents(planner_config)
        # invoke agents
        return self.agents_run(role_agents, planner_config, agent_model, planner_input)

        # 调用 agents_run 函数并传入事件
        # return self.agents_run_event(role_agents, planner_config, agent_model, planner_input, event)

    @staticmethod
    def generate_role_agents(planner_config: dict) -> dict:
        """Generate role agents."""
        # role = planner_config.get('role', {})
        role = planner_config.get('roles', {})
        LOGGER.info(f"role {role}")
        role_names = role.get('name', [])
        if len(role_names) == 0:
            raise NotImplementedError
        agents = dict()
        for role_name in role_names:
            agents[role_name] = AgentManager().get_instance_obj(role_name)
        return agents

    def agents_run(self, role_agents: dict, planner_config: dict, agent_model: AgentModel,
                   agent_input: dict) -> dict:
        """ Invoke the role agents and host agent.

        Args:
            role_agents (dict): role agents.
            planner_config (dict): Planner config.
            agent_model (AgentModel): Agent model object.
            agent_input (dict): Agent input object.
        Returns:
            dict: The planner result.
        """
        total_round: int = 1
        chat_history = []
        LOGGER.info(f"The topic of discussion is {agent_input.get(self.input_key)}")
        LOGGER.info(f"The role agents are {'|'.join(role_agents.keys())}")
        agent_input['total_round'] = total_round
        agent_input['roles'] = ' and '.join(role_agents.keys())

        LOGGER.info(f"agent_input \n{agent_input}")

        # event_dispatcher = agent_input["event"]
        for i in range(total_round):
            LOGGER.info("------------------------------------------------------------------")
            LOGGER.info(f"Start a discussion, round is {i + 1}.")

            # event_dispatcher.trigger_event("NEED_INPUT", {"msg":"需要用户输入"})

            # def get_user_input():
            #     agent_input['input'] = q = event_dispatcher.event_queue.get()
            #
            # event_dispatcher.register_listener("USER_INPUT",get_user_input)
            user_role = agent_input['role']
            # if user_role == '原告':
            #
            #     drama = {
            #         0: {'name': '法官','action': '开庭'},
            #         1: {'name': '原告方', 'action': '陈述'},
            #         2: {'name': '审判员', 'action': '判断原告方的陈述是否与当前背景有关'},
            #         3: {'name': '被告方律师', 'action': '陈述'},
            #         4: {'name': '审判员', 'action': '判断被告方的陈述是否与当前背景有关'},
            #         5: {'name': '原告方', 'action': '陈述'},
            #         6: {'name': '法官', 'action': '向两方提问'}
            #     }
            # elif user_role == '被告':
            #     drama = {
            #         0: {'name': '法官','action': '开庭'},
            #         1: {'name': '原告方律师', 'action': '陈述'},
            #         2: {'name': '审判员', 'action': '判断原告方的陈述是否与当前背景有关'},
            #         3: {'name': '被告方', 'action': '陈述'},
            #         4: {'name': '审判员', 'action': '判断被告方的陈述是否与当前背景有关'},
            #         5: {'name': '原告方律师', 'action': '陈述'},
            #         6: {'name': '法官', 'action': '向两方提问'}
            #     }
            # else:
            drama = {
                0: {'name': '法官','action': '开庭'},
                1: {'name': '原告方', 'action': '陈述'},
                2: {'name': '审判员', 'action': '判断原告方的陈述是否与当前背景有关'},
                3: {'name': '被告方', 'action': '陈述'},
                4: {'name': '审判员', 'action': '判断被告方的陈述是否与当前背景有关'},
                5: {'name': '原告方', 'action': '陈述'},
                6: {'name': '法官', 'action': '向两方提问'}
            }
            # agent_input['input'] = input()
            LOGGER.debug(f"role_agents {role_agents}")

            for stage in range(len(drama)):
                segment = drama[stage]
                role = segment['name']
                action = segment['action']

                agent_input['role'] = role
                agent_input['action'] = action

                agent = role_agents[role + '_agent']

                if role != user_role:
                    output_object: OutputObject = agent.run(**agent_input)

                    LOGGER.debug(f"output_object {output_object.to_dict()}")

                    current_output = output_object.get_data('output', '')
                else:
                    LOGGER.info("轮到用户输入")
                    # useri = """尊敬的法官大人，我是本案的原告，李明。今天站在这里，内心五味杂陈，既有对公正的渴望，也有对过去友情的惋惜。事情是这样的：我和王芳曾经是好朋友，关系甚密。2019年的春天，她来找我，说遇到了些经济上的困难，急需一笔钱周转。出于对朋友的信任和帮助的愿望，我毫不犹豫地借给了她十万元人民币。当时，我们并没有签订正式的合同，因为我觉得朋友之间不需要那么多手续，而且我们还有微信聊天记录作为借款的证明。然而，时间过得很快，转眼间还款期限到了。我曾多次联系王芳，提醒她还款的事情，但她总是找各种借口拖延，甚至后来连电话都不接了。这让我感到十分失望和无助。我并不是非要她立刻还清所有债务，但至少应该有个明确的态度和计划，而不是逃避。这笔钱对我来说很重要，它是我辛苦工作多年积攒下来的。我并不是要追究什么法律责任，只是希望能够得到一个公平的对待，让我的权益得到保障。我希望法庭能够理解我的处境，给予公正的裁决，让王芳能够认识到自己的责任，履行她的承诺。最后，我想说的是，我始终相信法律的公正，也愿意配合法庭的一切调查和安排。谢谢法官大人的聆听。
                    # """

                    current_output = input()
                    # current_output = useri
                # process chat history
                # 这行不能去掉    必须添加human的空输入
                # chat_history.append({'role':role,'type': role,'content': ''})
                chat_history.append({'role':role,'type': 'human','content': ''})

                cnt = f"\n第 {i + 1} 回合 role {role} 发言: \n{current_output}"
                # ai_msg = {'role': role, 'type': role, 'content': current_output}
                ai_msg = {'role': role, 'type': 'ai', 'content': current_output}
                chat_history.append(ai_msg)
                agent_input['chat_history'] = chat_history

                LOGGER.info("------------------------------------------------------------------")
                LOGGER.info(f"开始发言: agent is {role}.")
                LOGGER.info(cnt)
                # yield chat_history[-1]
                LOGGER.info(f" for {role} \n{agent_input}")
                LOGGER.info(f"agent_input['chat_history'] {agent_input['chat_history']}")
                LOGGER.info("------------------------------------------------------------------")

            # for agent_name, agent in role_agents.items():
            #     # invoke role agent
            #     agent_input['agent_name'] = agent_name
            #     agent_input['cur_round'] = i + 1
            #     agent_input['role'] = agent_name
            #     output_object: OutputObject = agent.run(**agent_input)
            #     LOGGER.debug(f"output_object {output_object.to_dict()}")
            #
            #
            #     current_output = output_object.get_data('output', '')
            #
            #     # process chat history
            #     chat_history.append({'role':'human','type': 'human','content': agent_input.get('input')})
            #
            #     cnt = f"第 {i + 1} 回合 agent {agent_name} 发言: {current_output}"
            #     ai_msg = {'role':agent_name,'type': 'ai','content': cnt}
            #     chat_history.append(ai_msg)
            #     agent_input['chat_history'] = chat_history
            #
            #     LOGGER.info("------------------------------------------------------------------")
            #     LOGGER.info(f"开始发言: agent is {agent_name}.")
            #     LOGGER.info(cnt)
            #     # yield chat_history[-1]
            #     LOGGER.info(f" for {agent_name} \n{agent_input}")
            #     LOGGER.info("------------------------------------------------------------------")

            # event_dispatcher.trigger_event("AGENT_CNT", cnt)
            # event_dispatcher.trigger_event("AGENT_CNT", {"msg": f"测试{i} {agent_name}"})
            # yield output_object

        agent_input['chat_history'] = chat_history

        for i in agent_input['chat_history']:
            LOGGER.info(f"re chat_history {i}")
        # yield chat_history
        # finally invoke host agent
        return self.invoke_host_agent(agent_model, agent_input)

    def invoke_host_agent(self, agent_model: AgentModel, planner_input: dict) -> dict:
        """ Invoke the host agent.

        Args:
            agent_model (AgentModel): Agent model object.
            planner_input (dict): Planner input object.
        Returns:
            dict: The planner result.
        """
        LOGGER.info("------------------------------------------------------------------")
        LOGGER.info(f"Discussion end.")
        LOGGER.info(f"Host agent starts summarize the discussion.")
        LOGGER.info("------------------------------------------------------------------")
        memory: ChatMemory = self.handle_memory(agent_model, planner_input)

        llm: LLM = self.handle_llm(agent_model)

        prompt: ChatPrompt = self.handle_prompt(agent_model, planner_input)
        process_llm_token(llm, prompt.as_langchain(), agent_model.profile, planner_input)

        chat_history = memory.as_langchain().chat_memory if memory else InMemoryChatMessageHistory()

        chain_with_history = RunnableWithMessageHistory(
            prompt.as_langchain() | llm.as_langchain(),
            lambda session_id: chat_history,
            history_messages_key="chat_history",
            input_messages_key=self.input_key,
        ) | StrOutputParser()
        res = asyncio.run(
            chain_with_history.ainvoke(input=planner_input, config={"configurable": {"session_id": "unused"}}))
        LOGGER.info(f"Discussion summary is: {res}")
        return {**planner_input, self.output_key: res, 'chat_history': generate_memories(chat_history)}

    def handle_prompt(self, agent_model: AgentModel, planner_input: dict) -> ChatPrompt:
        """Prompt module processing.

        Args:
            agent_model (AgentModel): Agent model object.
            planner_input (dict): Planner input object.
        Returns:
            ChatPrompt: The chat prompt instance.
        """
        profile: dict = agent_model.profile

        profile_prompt_model: AgentPromptModel = AgentPromptModel(introduction=profile.get('introduction'),
                                                                  target=profile.get('target'),
                                                                  instruction=profile.get('instruction'))

        # get the prompt by the prompt version
        prompt_version: str = profile.get('prompt_version')
        version_prompt: Prompt = PromptManager().get_instance_obj(prompt_version)

        if version_prompt is None and not profile_prompt_model:
            raise Exception("Either the `prompt_version` or `introduction & target & instruction`"
                            " in agent profile configuration should be provided.")
        if version_prompt:
            version_prompt_model: AgentPromptModel = AgentPromptModel(
                introduction=getattr(version_prompt, 'introduction', ''),
                target=getattr(version_prompt, 'target', ''),
                instruction=getattr(version_prompt, 'instruction', ''))
            profile_prompt_model = profile_prompt_model + version_prompt_model

        chat_prompt = ChatPrompt().build_prompt(profile_prompt_model, self.prompt_assemble_order)
        image_urls: list = planner_input.pop('image_urls', []) or []
        if image_urls:
            chat_prompt.generate_image_prompt(image_urls)
        return chat_prompt
