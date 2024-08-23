# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/20 19:39
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: graph.py
from typing import Optional, Any

import networkx as nx

from agentuniverse.workflow.node.enum import NodeEnum, NodeStatusEnum
from agentuniverse.workflow.node.node import Node
from agentuniverse.workflow.node.node_constant import NODE_CLS_MAPPING
from agentuniverse.workflow.node.node_output import NodeOutput
from agentuniverse.workflow.workflow_output import WorkflowOutput


class Graph(nx.DiGraph):
    """The basic class of the graph."""

    def build(self, workflow_id: str, config: dict) -> 'Graph':
        """Build the graph."""
        nodes_config = config.get('nodes')
        if not nodes_config:
            raise ValueError('The nodes configuration is empty')
        for node_config in nodes_config:
            self.add_graph_node(workflow_id, node_config)
        edges_config = config.get('edges')
        if not edges_config:
            raise ValueError('The edges configuration is empty')
        for edge_config in edges_config:
            self.add_graph_edge(edge_config)
        if not nx.is_directed_acyclic_graph(self):
            raise ValueError("The provided configuration does not form a DAG.")
        return self

    def add_graph_node(self, workflow_id: str, node_config: dict) -> None:
        if node_config.get('type') not in NodeEnum.to_value_list():
            raise ValueError('The node type is not supported')
        node_id = node_config.get('id')
        if self.has_node(node_id):
            return
        node_cls = NODE_CLS_MAPPING[node_config.get('type')]
        node_type = node_config.pop('type')

        node_instance = node_cls(type=NodeEnum.from_value(node_type), workflow_id=workflow_id, **node_config)
        self.add_node(node_id, instance=node_instance, type=node_type)

    def add_graph_edge(self, edge_config: dict) -> None:
        self.add_edge(edge_config.get('source'), edge_config.get('target'))

    def run(self, workflow_output: WorkflowOutput) -> None:
        sorted_nodes = list(nx.topological_sort(self))
        predecessor_node: Node | None = None
        while True:
            next_node = self._get_next_node(sorted_nodes, predecessor_node)
            if not next_node:
                break
            self._run_node(predecessor_node=predecessor_node, cur_node=next_node, workflow_output=workflow_output)
            if next_node.type == NodeEnum.END:
                break
            predecessor_node = next_node

    def _get_next_node(self, nodes: Any, predecessor_node: Optional[Node] = None) -> Optional[Node]:
        if not predecessor_node:
            for node_id in nodes:
                if self.nodes[node_id]['type'] == NodeEnum.START.value:
                    return self.nodes[node_id]['instance']
        else:
            successors = self.successors(predecessor_node.id)
            if not successors:
                return None
            # TODO 如果没有source handle, 则粗暴的选择source edge的第一个相关的边
            for s in successors:
                return self.nodes[s]['instance']

    def _run_node(self, predecessor_node: Optional[Node] = None, cur_node: Node = None,
                  workflow_output: WorkflowOutput = None) -> None:
        try:
            # TODO run node, result must have inputs, process_data, outputs, execution_metadata
            node_output = cur_node.run(workflow_output.workflow_parameters)
        except Exception as e:
            node_output = NodeOutput(
                status=NodeStatusEnum.FAILED,
                error=str(e)
            )
        # if node_output.outputs:
        #     for variable_key, variable_value in node_output.outputs.items():
        #         # TODO 拿到node 执行结果的 outputs dict append variables to variable pool recursively
        #         self._append_variables_recursively(
        #             variable_pool=workflow_run_state.variable_pool,
        #             node_id=cur_node.node_id,
        #             variable_key_list=[variable_key],
        #             variable_value=variable_value
        #         )
        workflow_output.workflow_node_results[cur_node.id] = node_output
