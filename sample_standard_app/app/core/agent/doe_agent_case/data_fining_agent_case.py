from agentuniverse.agent.agent import Agent
from agentuniverse.agent.input_object import InputObject


class DataFiningAgent(Agent):
    def input_keys(self) -> list[str]:
        return ['source_path','input']

    def output_keys(self) -> list[str]:
        return []

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        for key in self.input_keys():
            agent_input[key] = input_object.get_data(key)
        return agent_input

    def parse_result(self, planner_result: dict) -> dict:
        return planner_result

    def execute(self, input_object: InputObject, agent_input: dict) -> dict:
        # 1. 智能体分析需要财报中的哪些数据
        # 2. 获取营收、利润数据、市场占比、获取公司的主营业务、获取公司赛道
        # 3. 获取公司的主营业务、管理层的讨论与分析

        return {}
