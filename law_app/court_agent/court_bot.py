from agentuniverse.base.agentuniverse import AgentUniverse
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager

AgentUniverse().start(config_path='../config/config.toml')


def chat(question: str):
    instance: Agent = AgentManager().get_instance_obj('court_agent')
    instance.run(input=question)


if __name__ == '__main__':
    chat("甜粽子好吃还是咸粽子好吃")