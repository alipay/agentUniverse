from agentuniverse.agent.agent import Agent
from agentuniverse.agent.input_object import InputObject


class DOEExpressingAgent(Agent):
    def input_keys(self) -> list[str]:
        return ['fund_info', 'product_track', 'interpret_latitude', 'argument_direction', 'argument_direction_list',
                'expression_techniques']

    def output_keys(self) -> list[str]:
        return []

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        for key in self.input_keys():
            agent_input[key] = input_object.get_data(key)
        return agent_input

    def parse_result(self, planner_result: dict) -> dict:
        return planner_result
