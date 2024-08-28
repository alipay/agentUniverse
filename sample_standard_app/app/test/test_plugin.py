import unittest

from agentuniverse.base.agentuniverse import AgentUniverse
from agentuniverse_product.agentuniverse_product import AgentUniverseProduct
from agentuniverse_product.service.model.plugin_dto import OPENAPISPluginDTO
from agentuniverse_product.service.plugin_service.plugin_service import PluginService
from agentuniverse_product.service.util.plugin_util import parse_openapi_yaml_to_tool_bundle


arxiv = """
info:
    description: arxiv查找论文
    title: arxiv_app
    version: v1
openapi: 3.0.1
paths:
    /arxiv:
        get:
            operationId: search
            parameters:
                - description: 输入搜索关键词，必须是英文
                  in: query
                  name: search_query
                  required: true
                  schema:
                    type: string
                - description: 搜索数量
                  in: query
                  name: count
                  schema:
                    type: integer
                - description: 可以是1:降序2:升序
                  in: query
                  name: sort_order
                  schema:
                    type: integer
                - description: 可以是1:相关性2.lastUpdateDate3.submittedDate
                  in: query
                  name: sort_by
                  schema:
                    type: integer
                - description: 报告编号过滤器，用于获取报告编号中包含给定关键字的结果
                  in: query
                  name: report_number
                  schema:
                    type: string
                - description: 主题类别过滤器，用于获取主题类别中包含给定关键字的结果。
                  in: query
                  name: subject_category
                  schema:
                    type: string
                - description: 标题过滤器，用于获取标题包含给定关键字的结果
                  in: query
                  name: title
                  schema:
                    type: string
                - description: 摘要过滤器，用于获取摘要中包含给定关键字的结果
                  in: query
                  name: abstract
                  schema:
                    type: string
                - description: 作者过滤器，用于获取包含给定关键字的作者的结果
                  in: query
                  name: author
                  schema:
                    type: string
                - description: 评论过滤器，用于获取评论中包含给定关键字的结果
                  in: query
                  name: comment
                  schema:
                    type: string
                - description: 期刊参考过滤器，用于获取期刊参考中包含给定关键字的结果
                  in: query
                  name: journal_reference
                  schema:
                    type: string
            requestBody:
                content:
                    application/json:
                        schema:
                            type: object
            responses:
                "200":
                    content:
                        application/json:
                            schema:
                                properties:
                                    items:
                                        items:
                                            properties:
                                                authors:
                                                    description: 作者列表
                                                    items:
                                                        description: 作者
                                                        type: string
                                                    type: array
                                                entry_id:
                                                    description: https://arxiv.org/abs/{id} 链接
                                                    type: string
                                                pdf_url:
                                                    description: pdf 下载链接
                                                    type: string
                                                published:
                                                    description: 发表时间
                                                    type: string
                                                summary:
                                                    description: 摘要
                                                    type: string
                                                title:
                                                    description: 标题
                                                    type: string
                                            type: object
                                        type: array
                                    total:
                                        description: 结果数目
                                        type: integer
                                type: object
                    description: new desc
                default:
                    description: ""
            summary: search
    /test:
        get:
            operationId: search
            parameters:
                - description: 输入搜索关键词，必须是英文
                  in: query
                  name: search_query
                  required: true
                  schema:
                    type: string
                - description: 搜索数量
                  in: query
                  name: count
                  schema:
                    type: integer
                - description: 可以是1:降序2:升序
                  in: query
                  name: sort_order
                  schema:
                    type: integer
                - description: 可以是1:相关性2.lastUpdateDate3.submittedDate
                  in: query
                  name: sort_by
                  schema:
                    type: integer
                - description: 报告编号过滤器，用于获取报告编号中包含给定关键字的结果
                  in: query
                  name: report_number
                  schema:
                    type: string
                - description: 主题类别过滤器，用于获取主题类别中包含给定关键字的结果。
                  in: query
                  name: subject_category
                  schema:
                    type: string
                - description: 标题过滤器，用于获取标题包含给定关键字的结果
                  in: query
                  name: title
                  schema:
                    type: string
                - description: 摘要过滤器，用于获取摘要中包含给定关键字的结果
                  in: query
                  name: abstract
                  schema:
                    type: string
                - description: 作者过滤器，用于获取包含给定关键字的作者的结果
                  in: query
                  name: author
                  schema:
                    type: string
                - description: 评论过滤器，用于获取评论中包含给定关键字的结果
                  in: query
                  name: comment
                  schema:
                    type: string
                - description: 期刊参考过滤器，用于获取期刊参考中包含给定关键字的结果
                  in: query
                  name: journal_reference
                  schema:
                    type: string
            requestBody:
                content:
                    application/json:
                        schema:
                            type: object
            responses:
                "200":
                    content:
                        application/json:
                            schema:
                                properties:
                                    items:
                                        items:
                                            properties:
                                                authors:
                                                    description: 作者列表
                                                    items:
                                                        description: 作者
                                                        type: string
                                                    type: array
                                                entry_id:
                                                    description: https://arxiv.org/abs/{id} 链接
                                                    type: string
                                                pdf_url:
                                                    description: pdf 下载链接
                                                    type: string
                                                published:
                                                    description: 发表时间
                                                    type: string
                                                summary:
                                                    description: 摘要
                                                    type: string
                                                title:
                                                    description: 标题
                                                    type: string
                                            type: object
                                        type: array
                                    total:
                                        description: 结果数目
                                        type: integer
                                type: object
                    description: new desc
                default:
                    description: ""
            summary: search
servers:
    - url: http://exp-tech.plugin.knowledgepie.cn
"""

class UtilsTest(unittest.TestCase):
    """
    Test cases for the SQLDBWrapper
    """
    def setUp(self) -> None:
        AgentUniverse().start(config_path='../../config/config.toml',core_mode=True)

    def test_util(self):
        plugin_dto = OPENAPISPluginDTO(nickname='test_plugin', avatar='test_avatar', id='test_plugin',
                                       description='test',openapi_desc = arxiv,toolset=['arxiv','test'])
        PluginService().create_plugin_with_openapi(plugin_dto)
if __name__ == '__main__':
    unittest.main()