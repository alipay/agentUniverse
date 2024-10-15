from typing import Optional

import requests
from bs4 import BeautifulSoup

from agentuniverse.agent.action.tool.tool import Tool, ToolInput


class LoadFundInfoTool(Tool):
    fund_info_url: Optional[str] = "https://fund.pingan.com/main/peanutFinance/yingPeanut/fundDetailV2/"

    fund_rate_info_url: Optional[str] = "https://fund.eastmoney.com/"

    def execute(self, tool_input: ToolInput):
        fund_id = tool_input.get_data("fund_id")
        fund_info_url = f"{self.fund_info_url}{fund_id}.shtml"
        # 爬取页面中基金的信息
        response = requests.get(fund_info_url)
        response.encoding = "utf-8"
        html_content = response.text

        rate_info_url = f"{self.fund_rate_info_url}{fund_id}.html"

        response = requests.get(rate_info_url)
        response.encoding = "utf-8"
        rate_html_content = response.text
        soup = BeautifulSoup(rate_html_content, "html.parser")
        # elem = soup.find("table", class_="ui-table-hover")
        elem = soup.find("li", id="increaseAmount_stage").find("table", class_="ui-table-hover")
        # print(str(elem.contents))
        html_content = html_content + "\n========================================\n" + str(elem.contents)
        return html_content

# import requests
# from bs4 import BeautifulSoup, Tag
#
# if __name__ == '__main__':
#     from langchain_community.document_loaders import UnstructuredHTMLLoader
#
#     # loader = BSHTMLLoader("example_data/fake-content.html")
#     # data = loader.load()
#     # print(data)
#     response = requests.get("https://fund.pingan.com/main/peanutFinance/yingPeanut/fundDetailV2/000759.shtml")
#     response.encoding = "utf-8"
#     html_content = response.text
#     soup = BeautifulSoup(html_content, "html.parser")
#     # 获取 class 为 fund-base, fund-manager,fund-info的组件
#     fund_base_info = soup.find("div", class_="fund-base")
#
#     fund_quotation = fund_base_info.find("div", class_="fund-quotation")
#
#     for elem in fund_quotation.children:
#         # 检查元素是否是Tag实例
#         if isinstance(elem, Tag):
#             classes = elem.get("class")
#             if classes and "quotation-top" in classes:
#                 print(classes)  # 打印类列表
#             else:
#                 print("Element has no class attribute.")
#         else:
#             # 如果不是Tag实例，那么可能是NavigableString或其他类型的节点
#             print("This is not a Tag, so it doesn't have a class attribute.")
#
#     # print(fund_quotation.children)
#
#
#
#
#     # fund_manager_info = soup.find("div", class_="fund-manager").text
#     # fund_info = soup.find("div", class_="fund-info")
#
#     # 获取fund_info div的所有信息子组件
#     # print(str(fund_info))
#
#     # print(len(fund_base_info)+len(fund_manager_info)+len(fund_info_info))
