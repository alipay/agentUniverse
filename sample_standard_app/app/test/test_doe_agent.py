import json
import unittest

import pandas as pd
import pdfplumber

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.base.agentuniverse import AgentUniverse


class DOEAgentTestCase(unittest.TestCase):
    def setUp(self) -> None:
        AgentUniverse().start(config_path='../../config/config.toml')

    def test_serial_agent(self):
        tables = self.extract_tables_from_pdf("/Users/weizj/Documents/GitHub/agentUniverse/sample_standard_app/app/test/doe_data/document.pdf")
        self.save_tables_to_csv(tables, output_prefix="table")
        # agent_instance: Agent = AgentManager().get_instance_obj('serial_agent')
        # output = agent_instance.run(
        #     input='上海今天的天气怎么样',
        #     image='https://www.baidu.com/img/PCtm_d9c8750bed0b3c7d089fa7d55720d6cf.png',
        # )
        # print(json.dumps(
        #     output.to_dict(),
        #     ensure_ascii=False
        # ))

    def extract_tables_from_pdf(self,pdf_path):
        """
        从PDF中提取所有表格，并将其转换为Pandas DataFrame格式。
        """
        tables = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    # 提取每一页的所有表格
                    print(page.extract_text())
                    page_tables = page.extract_tables()
                    for table in page_tables:
                        # 将表格转换为DataFrame
                        if table:
                            df = pd.DataFrame(table)
                            tables.append(df)
        except Exception as e:
            print(f"Error reading tables from PDF: {e}")
        return tables

    def save_tables_to_csv(self,tables, output_prefix="output_table"):
        """
        将提取的所有表格保存到CSV文件中。
        """
        for idx, table in enumerate(tables):
            # 生成文件名，并将表格保存为CSV
            table.to_csv(f"./doe_data/{output_prefix}_{idx + 1}.csv", index=False, header=False)
            print(f"Table {idx + 1} saved to {output_prefix}_{idx + 1}.csv")


if __name__ == '__main__':
    unittest.main()
