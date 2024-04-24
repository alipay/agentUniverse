# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/28 17:44
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: test_peer_agent.py
import unittest

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.base.agentuniverse import AgentUniverse


class PeerAgentTest(unittest.TestCase):
    """
    Test cases for the overall process of peer agents
    """

    def setUp(self) -> None:
        AgentUniverse().start(config_path='../../config/config.toml')

    def test_planning_agent(self):
        """Test demo planning agent."""
        instance: Agent = AgentManager().get_instance_obj('demo_planning_agent')
        output_object: OutputObject = instance.run(input='分析下巴菲特减持比亚迪的原因')
        print(output_object.get_data('output'))

    def test_executing_agent(self):
        """Test demo executing agent.

        Note:
            This agent uses `demo_tool`, which is a simple Google search.
            You need to sign up for a free account at https://serper.dev
            and get the serpher api key (2500 free queries).
        """
        instance: Agent = AgentManager().get_instance_obj('demo_executing_agent')
        # demo planning agent result, which is a framework of mind solving the final problem.
        framework = ["巴菲特减持比亚迪的具体情况是什么？包括减持的时间和数量。",
                     "巴菲特减持比亚迪前后的市场环境是怎么样的？",
                     "巴菲特的投资策略是什么？是否可能影响其决定减持比亚迪？",
                     "比亚迪在巴菲特减持前后的业绩表现如何？",
                     "当时的市场走势是怎样的？是否可能影响巴菲特的决定？",
                     "巴菲特减持比亚迪对比亚迪的影响有哪些？比如可能的股价变动、投资者信心等。",
                     "巴菲特减持比亚迪对相关市场有哪些影响？"]
        planning_result = InputObject({'framework': framework})
        output_object: OutputObject = instance.run(input='分析下巴菲特减持比亚迪的原因',
                                                   planning_result=planning_result)
        print(output_object.get_data('executing_result'))

    def test_expressing_agent(self):
        """Test demo expressing agent."""
        instance: Agent = AgentManager().get_instance_obj('demo_expressing_agent')

        # demo executing agent result
        executing_list = [{'input': '巴菲特减持比亚迪的具体情况是什么？包括减持的时间和数量。',
                           'output': '巴菲特通过其旗下的伯克希尔·哈撒韦公司，自2022年8月24日开始，对比亚迪H股进行了多次减持。具体来说，这是他们第12次披露减持比亚迪的消息。在最近一次的减持中，伯克希尔·哈撒韦的持股比例从9.21%降至8.98%，平均减持价格为每股266.85港元，总共套现约6.76亿港元。尽管巴菲特的减持速度和力度都有加快的趋势，但整体来看，比亚迪的股价并未受到太大影响。实际上，这一次披露的减持均价，是近7次披露中的最高价格。'},
                          {'input': '巴菲特减持比亚迪前后的市场环境是怎么样的？',
                           'output': '巴菲特减持比亚迪的市场环境主要可以从以下几个方面来分析：\n\n首先，巴菲特减持比亚迪的消息在资本市场上引起了广泛的关注，这一事件被视为新能源赛道的重要风向标。如果市场能够澄清相关的传闻，那么这无疑将对新能源赛道的持续看好产生积极影响。反之，如果确认巴菲特大举减持，可能会对新能源赛道的前景产生一定的影响。\n\n其次，巴菲特的投资策略一直是市场关注的焦点。他的投资策略主要是基于公司的运营结果，而非短期的股市波动。因此，巴菲特减持比亚迪可能是他对比亚迪的运营状况或者新能源行业的前景产生了新的认识。\n\n再次，巴菲特减持比亚迪的消息发布之后，可能会引发市场的情绪波动。根据巴菲特的"市场先生"寓言，市场的短期走势往往受到投资者情绪的影响，而长期价值则取决于公司的经济进步。因此，巴菲特减持比亚迪可能会引发市场的短期情绪波动，但长期来看，比亚迪的股价还是会回归其经济价值。\n\n最后，巴菲特减持比亚迪的行为可能会影响其他投资者的决策。因为巴菲特的投资决策往往会被市场视为重要的参考，他的减持行为可能会引发其他投资者的跟风行为，从而影响比亚迪的股价。\n\n总结来说，巴菲特减持比亚迪的市场环境是复杂的，它受到市场对新能源赛道的看好、巴菲特的投资策略、市场情绪波动以及其他投资者行为的影响。'},
                          {'input': '巴菲特的投资策略是什么？是否可能影响其决定减持比亚迪？',
                           'output': '巴菲特的投资策略主要是价值投资，以长期持有为主，并且他非常注重企业的内在价值和市场价格。他会对他感兴趣并且理解的企业进行深入研究，变成该领域的专家，并且他会和企业管理层进行合作，而不是对抗。他的投资策略主要包含以下几个方面：\n\n1. 不跟随股市的日常波动。他认为市场只是为了方便买卖，而不是设定价值。\n2. 不尝试分析或担忧整体经济。如果你不能预测股市的日常波动，那么你如何可靠地预测经济的命运？\n3. 购买一家企业，而不仅仅是它的股票。他会把购买股票当作是购买整个企业，他会根据以下几个方面来评估企业：企业是否简单并且从投资者的角度来看是否可理解？企业是否有一致的运营历史？企业是否有良好的长期前景？管理层是否理性？管理层是否对股东坦诚？关注企业的回报率，而不是每股收益。寻找利润率高的公司。对于每一美元的留存收益，公司是否创造了至少一美元的额外市场价值？\n4. 管理一组企业。聪明的投资意味着具有商业所有者的优先级（专注于长期价值）而不是股票交易员（专注于短期的收益和损失）。\n\n对于巴菲特是否会继续减持比亚迪股份，我们可以结合他的投资策略来分析。首先，巴菲特是一个长期投资者，他不会因为短期的市场波动而轻易改变他的持股策略。其次，他非常注重企业的内在价值，如果他认为比亚迪的内在价值依然存在，那么他可能会继续持有。但是，如果他认为比亚迪的内在价值已经不再，或者市场价格已经远超过了他认为的合理价值，那么他可能会选择减持。'},
                          {'input': '比亚迪在巴菲特减持前后的业绩表现如何？',
                           'output': '比亚迪在巴菲特减持前后的业绩表现均表现出色。在巴菲特减持的同时，比亚迪的业绩表现仍然非常突出。在新能源汽车领域，比亚迪已经明显领先于对手。其前三季度的营业收入达到了2676.88亿元，同比增长了84.37%，这主要是因为新能源汽车业务的增长。\n\n此外，比亚迪在10月30日晚公布的三季报中显示，其前三季度实现营业收入4222.75亿元，同比增长58%，实现净利润213.67亿元，同比增长130%，业绩保持高速增长态势。这些数据显示，即使在巴菲特减持的情况下，比亚迪的业绩仍然在稳步增长，这也是多个证券机构对比亚迪持续保持买入评级的重要原因。'},
                          {'input': '当时的市场走势是怎样的？是否可能影响巴菲特的决定？',
                           'output': '根据提供的信息，没有直接描述当时的市场走势是怎样的，也没有明确指出市场走势是否影响了巴菲特的决定。但从巴菲特的投资策略来看，他的决策更多地是基于对公司的长期价值评估，而不是短期的市场波动。他的投资哲学是，长期来看，股票的价值最终将反映出公司的经济表现，而不是日常市场波动。\n\n巴菲特的策略是，即使股票价值下跌50%或更多，也要保持冷静，因为这是增加投资组合份额的好机会，只要投资的公司基本面健康，管理良好，价格合理，市场最终会认可其成功。\n\n因此，从这个角度看，即使市场走势对巴菲特的决策有影响，也只是在他评估公司价值的基础上，作为买入或持有股票的时机考虑，而不会改变他的基本投资策略。'},
                          {'input': '巴菲特减持比亚迪对比亚迪的影响有哪些？比如可能的股价变动、投资者信心等。',
                           'output': '巴菲特减持比亚迪的行为可能对比亚迪产生以下几方面的影响：\n\n1. 股价变动：巴菲特减持比亚迪可能会引发市场对比亚迪股价的质疑，导致股价下跌。因为巴菲特的投资决策通常被市场视为信号，他的减持行为可能被解读为对比亚迪未来盈利能力的不确定性。\n\n2. 投资者信心：巴菲特减持比亚迪可能会影响投资者对比亚迪的信心。巴菲特是一位著名的价值投资者，他的投资决策通常会影响其他投资者的决策。如果他减持比亚迪，可能会引发其他投资者对比亚迪未来的担忧，进而影响他们的投资决策。\n\n3. 公司声誉：巴菲特减持比亚迪可能会对比亚迪的声誉造成一定影响。因为巴菲特是一位世界级的投资大师，他的投资决策通常会被媒体广泛报道，这可能会引起公众对比亚迪的关注，进而影响比亚迪的声誉。\n\n4. 公司经营：巴菲特减持比亚迪可能会对比亚迪的经营产生影响。如果市场对比亚迪的信心下降，可能会影响比亚迪的融资能力，进而影响其经营。\n\n总的来说，巴菲特减持比亚迪可能会对比亚迪的股价、投资者信心、公司声誉和经营产生影响。然而，这些影响的具体程度会受到许多因素的影响，包括巴菲特减持的比例、市场对比亚迪的其他信息的反应等。'},
                          {'input': '巴菲特减持比亚迪对相关市场有哪些影响？',
                           'output': '巴菲特减持比亚迪的决定对相关市场可能产生以下影响：\n\n1. 投资者心理影响：巴菲特是世界知名的投资大师，他的投资决策往往会对市场产生影响。他首次减持比亚迪，可能会在持有新能源汽车股票的投资者心理上产生影响，引发部分投资者对新能源汽车市场的担忧和不确定性。\n\n2. 股价波动：巴菲特减持比亚迪的消息可能会导致比亚迪的股价出现波动。一方面，这可能是因为市场对比亚迪的前景产生了疑虑；另一方面，可能是因为一些投资者在跟风巴菲特的决策，选择减持比亚迪股票。\n\n3. 市场信心下滑：由于比亚迪是新能源汽车市场的重要参与者，因此巴菲特减持比亚迪可能会导致市场对新能源汽车市场的信心下滑，影响新能源汽车市场的整体发展。\n\n4. 投资主线调整：巴菲特减持比亚迪可能会引发投资者对新能源汽车投资主线的重新思考。投资者可能会重新评估新能源汽车市场的前景，并据此调整自己的投资策略。\n\n需要注意的是，这些影响可能会受到许多因素的影响，包括比亚迪的业绩、市场环境、投资者心理等。因此，投资者需要根据自己的判断和风险承受能力来做出投资决策。'}]

        executing_result = InputObject({'executing_result': executing_list})

        output_object: OutputObject = instance.run(input='分析下巴菲特减持比亚迪的原因',
                                                   executing_result=executing_result)
        print(output_object.get_data('output'))

    def test_reviewing_agent(self):
        """Test demo reviewing agent."""
        instance: Agent = AgentManager().get_instance_obj('demo_reviewing_agent')

        # demo expressing agent result
        expressing_output = """
        分析巴菲特减持比亚迪的原因，我们可以从以下几个角度进行解读：

        首先，从投资策略的角度来看，巴菲特一直以来的投资原则是“买入并持有”，而非频繁交易。他的投资决策通常基于对公司运营状况的长期观察和判断。因此，巴菲特减持比亚迪可能是他对比亚迪的未来发展或者新能源行业的前景有了新的认识。这可能是由于比亚迪的业务表现、市场竞争环境、政策风险等因素的变化，使得巴菲特对比亚迪的价值预期发生了调整。

        其次，从资本运作的角度来看，巴菲特减持比亚迪也可能是出于资本运作的需要。巴菲特的伯克希尔·哈撒韦公司是一个多元化的投资集团，需要对各个投资项目进行合理的资金配置。因此，巴菲特可能是在进行资产配置的调整，以适应市场环境的变化，或者获取更高的投资回报。

        再次，从市场环境的角度来看，近年来，新能源汽车行业的竞争日益激烈，各大汽车厂商纷纷投入新能源汽车的研发和生产。在这种情况下，巴菲特可能认为比亚迪在未来的市场竞争中面临的压力和挑战增大，因此选择了减持。

        总的来说，巴菲特减持比亚迪的原因可能是多方面的，包括他对比亚迪及新能源行业未来发展的认识变化，资本运作的需要，以及市场环境的变化等。这些因素的综合作用可能导致了巴菲特对比亚迪的投资策略进行了调整。
        """
        expressing_result = InputObject({'output': expressing_output})

        output_object: OutputObject = instance.run(input='分析下巴菲特减持比亚迪的原因',
                                                   expressing_result=expressing_result)
        print(output_object.get_data('output'))

    def test_peer_agent(self):
        """Test demo peer agent.

        The overall process of peer agents (demo_planning_agent/demo_executing_agent/demo_expressing_agent/demo_reviewing_agent).
        """
        instance: Agent = AgentManager().get_instance_obj('demo_peer_agent')
        output_object: OutputObject = instance.run(input='分析下巴菲特减持比亚迪的原因')
        print(output_object.get_data('output'))


if __name__ == '__main__':
    pass
