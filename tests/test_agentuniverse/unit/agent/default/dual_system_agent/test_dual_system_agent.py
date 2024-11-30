# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Test cases for the dual system agent."""

import unittest
from typing import List, Dict, Any, Optional
import os
import json
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.base.agentuniverse import AgentUniverse
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.annotation.singleton import singleton
from agentuniverse.agent_serve.service_manager import ServiceManager
from agentuniverse.workflow.workflow_manager import WorkflowManager
from agentuniverse.prompt.prompt_manager import PromptManager
from agentuniverse.llm.llm_manager import LLMManager
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.agent.action.knowledge.knowledge_manager import KnowledgeManager
from agentuniverse.agent.action.knowledge.embedding.embedding_manager import EmbeddingManager
from agentuniverse.agent.action.knowledge.query_paraphraser.query_paraphraser_manager import QueryParaphraserManager
from agentuniverse.agent.action.knowledge.doc_processor.doc_processor_manager import DocProcessorManager
from agentuniverse.agent.action.knowledge.store.store_manager import StoreManager
from agentuniverse.agent.action.knowledge.rag_router.rag_router_manager import RagRouterManager
from agentuniverse.agent.action.knowledge.reader.reader_manager import ReaderManager
from agentuniverse.agent.plan.planner.planner_manager import PlannerManager
from agentuniverse.agent.memory.memory_manager import MemoryManager

class DualSystemAgentTest(unittest.TestCase):
    """Test cases for the dual system (fast/slow thinking) agent."""
    
    agent: Optional[Agent] = None
    task_results: Dict[str, OutputObject] = {}

    @classmethod
    def setUpClass(cls) -> None:
        """Set up test environment once for all test methods."""    
        # 启动 AgentUniverse
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.toml')
        AgentUniverse().start(config_path=config_path)
        cls.agent = AgentManager().get_instance_obj('DualSystemAgent')
        cls.task_results = {}

    def setUp(self) -> None:
        """Set up for each test method."""
        pass

    def run_task(self, query: str, task_id: str) -> OutputObject:
        """Run a task with the dual system agent."""
        input_obj = {
            "input":query,
            "task_id":task_id or f"test_task_{len(self.__class__.task_results)}",
        }
        output_obj: OutputObject = self.__class__.agent.run(**input_obj)
        self.__class__.task_results[input_obj['task_id']] = output_obj
        return output_obj

    def test_system1_fast_thinking(self) -> None:
        """Test fast thinking system."""
        # Case 1: Simple calculation (简单计算)
        result = self.run_task('What is 2 + 2?', 'fast_calculation')
        self.assertEqual(result.get_data('system_type'), 'fast_thinking')
        self.assertGreaterEqual(result.get_data('confidence'), 0.7)
        self.assertIn('4', result.get_data('output'))
        
        # Case 2: Common knowledge with high confidence (简单常识)
        result = self.run_task('What is the capital of China?', 'common_knowledge')
        self.assertEqual(result.get_data('system_type'), 'fast_thinking')
        self.assertGreaterEqual(result.get_data('confidence'), 0.9)
        self.assertIn('Beijing', result.get_data('output'))
        
        # Case 3: Simple definition question (简单定义)
        result = self.run_task('GDP 的定义是什么', 'common_knowledge')
        self.assertEqual(result.get_data('system_type'), 'fast_thinking')
        self.assertGreaterEqual(result.get_data('confidence'), 0.7)

    def test_system2_slow_thinking(self) -> None:
        """Test slow thinking system."""
        # Case 1: Complex analysis (复杂分析)
        result = self.run_task(
            '分析一下为什么近期黄金价格持续上涨，并预测未来走势如何？',
            'complex_analysis'
        )
        self.assertEqual(result.get_data('system_type'), 'slow_thinking')
        
        # Case 2: Multi-factor evaluation (多因素评估)
        result = self.run_task(
            '请评估人工智能在未来5年内对就业市场的潜在影响，考虑技术发展、劳动力市场变化和教育体系适应性等因素。',
            'complex_evaluation'
        )
        self.assertEqual(result.get_data('system_type'), 'slow_thinking')
        
        # Case 3: Context-dependent question (上下文依赖)
        result = self.run_task(
            '考虑到这些因素的影响，它们将如何改变我们的生活方式？',
            'context_dependent'
        )
        self.assertEqual(result.get_data('system_type'), 'slow_thinking')

    def test_borderline_cases(self) -> None:
        """Test cases that are on the border between fast and slow thinking."""
        # Case 1: Moderate complexity with low confidence
        result = self.run_task('黄金后面还涨不涨了?', 'borderline_confidence')
        print(f"Result: {json.dumps(result.to_dict(), ensure_ascii=False)}")
        self.assertEqual(result.get_data('system_type'), 'slow_thinking')
        
        # Case 2: Simple question with context
        result = self.run_task('这个问题的答案是什么？', 'simple_with_context')
        self.assertEqual(result.get_data('system_type'), 'slow_thinking')

if __name__ == '__main__':
    unittest.main()
