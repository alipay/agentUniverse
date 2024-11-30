# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Test cases for the dual system agent."""

import unittest
from typing import List, Dict, Any
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
from agentuniverse.database.sqldb_wrapper_manager import SQLDBWrapperManager
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

    def setUp(self) -> None:
        """Set up test environment."""
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.toml')
        AgentUniverse().start(config_path=config_path)
        self.agent: Agent = AgentManager().get_instance_obj('DualSystemAgent')
        self.task_results: Dict[str, OutputObject] = {}


    def run_task(self, query: str, task_id: str) -> OutputObject:
        """Run a task with the dual system agent."""
        input_obj = {
            "input":query,
            "task_id":task_id or f"test_task_{len(self.task_results)}",
        }
        output_obj: OutputObject = self.agent.run(**input_obj)
        self.task_results[input_obj['task_id']] = output_obj
        return output_obj

    def test_system1_fast_thinking(self) -> None:
        # Case 1: Simple calculation
        result = self.run_task('What is 2 + 2?', 'fast_calculation')
        self.assertEqual(result.get_data('system_type'), 'fast_thinking')
        self.assertGreaterEqual(result.get_data('confidence'), 0.7)
        self.assertIn('4', result.get_data('output'))
        
        # Case 2: Common knowledge with high confidence
        result = self.run_task('What is the capital of China?', 'common_knowledge')
        self.assertEqual(result.get_data('system_type'), 'fast_thinking')
        self.assertGreaterEqual(result.get_data('confidence'), 0.9)
        self.assertIn('Beijing', result.get_data('output'))
        
        # Case 3: Common knowledge with high confidence
        result = self.run_task('GDP 的定义是什么', 'common_knowledge')
        self.assertEqual(result.get_data('system_type'), 'fast_thinking')
        self.assertGreaterEqual(result.get_data('confidence'), 0.7)
        
        # Case 4: Borderline confidence case
        result = self.run_task('黄金后面还涨不涨了?', 'borderline_confidence')
        print(f"Result: {json.dumps(result.to_dict(), ensure_ascii=False)}")
        # Should switch to slow thinking due to uncertainty
        self.assertEqual(result.get_data('system_type'), 'slow_thinking')
        # self.assertEqual(result.get_data('output'), 'This is a mock response')

if __name__ == '__main__':
    unittest.main()
