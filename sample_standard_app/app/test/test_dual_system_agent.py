# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Test cases for the dual system agent."""

import unittest
from typing import List, Dict, Any
import os

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

    def setUp(self):
        """Set up test environment."""
        # Clear all singleton instances
        from agentuniverse.base.annotation.singleton import singleton
        singleton.instances = {}  # Clear all singleton instances

        # Get the absolute path to the config file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, '../../config/config.toml')
        
        # Start AgentUniverse with the config
        AgentUniverse().start(config_path=config_path)
        self.agent: Agent = AgentManager().get_instance_obj('demo_dual_system_agent')
        self.stream_outputs: List[Dict[str, Any]] = []
        self.task_results = {}

    def stream_callback(self, output: Dict[str, Any]) -> None:
        """Callback function for stream output.
        
        Args:
            output: Stream output data
        """
        self.stream_outputs.append(output)

    def run_task(self, input_text: str, task_type: str) -> OutputObject:
        """Run a task with the dual system agent."""
        input_obj = InputObject(params={'input': input_text, 'stream_callback': self.stream_callback})
        output_obj = self.agent.run(input_obj)
        self.task_results[task_type] = output_obj
        return output_obj

    def test_system1_fast_thinking(self):
        """Test System 1 (Fast Thinking) with simple tasks.
        
        Test cases:
        1. Simple calculations
        2. Common knowledge queries
        3. Pattern matching responses
        4. Confidence threshold checking
        """
        # Case 1: Simple calculation
        result = self.run_task('What is 2 + 2?', 'fast_calculation')
        self.assertEqual(result.get_data('system_type'), 'fast')
        self.assertGreaterEqual(result.get_data('confidence'), 0.7)
        self.assertIn('4', result.get_data('output'))
        
        # Verify stream output
        self.assertTrue(any(output.get('type') == 'fast_thinking' 
                          for output in self.stream_outputs))
        
        # Case 2: Common knowledge with high confidence
        self.stream_outputs.clear()
        result = self.run_task('What is the capital of China?', 'common_knowledge')
        self.assertEqual(result.get_data('system_type'), 'fast')
        self.assertGreaterEqual(result.get_data('confidence'), 0.7)
        self.assertIn('Beijing', result.get_data('output'))
        
        # Case 3: Pattern matching with very high confidence
        self.stream_outputs.clear()
        result = self.run_task('Hello!', 'pattern_matching')
        self.assertEqual(result.get_data('system_type'), 'fast')
        self.assertGreaterEqual(result.get_data('confidence'), 0.9)
        
        # Case 4: Borderline confidence case
        self.stream_outputs.clear()
        result = self.run_task('What is the third most populous city in France?', 'borderline_confidence')
        # Should switch to slow thinking due to uncertainty
        self.assertEqual(result.get_data('system_type'), 'slow')

    def test_system2_slow_thinking(self):
        """Test System 2 (Slow Thinking) with complex tasks.
        
        Test cases:
        1. Analysis tasks
        2. Multi-step reasoning
        3. Creative tasks
        4. Stream output verification
        """
        # Case 1: Complex analysis
        result = self.run_task('Analyze the potential impact of quantum computing on cybersecurity.', 'complex_analysis')
        self.assertEqual(result.get_data('system_type'), 'slow')
        
        # Verify PEER system execution
        stream_types = [output.get('type') for output in self.stream_outputs]
        self.assertIn('planning', stream_types)
        self.assertIn('executing', stream_types)
        self.assertIn('expressing', stream_types)
        
        # Case 2: Multi-step reasoning
        self.stream_outputs.clear()
        result = self.run_task('Design a strategy to reduce urban traffic congestion.', 'multi_step_reasoning')
        self.assertEqual(result.get_data('system_type'), 'slow')
        self.assertTrue(any(output.get('type') == 'planning' 
                          for output in self.stream_outputs))
        
        # Case 3: Creative task
        self.stream_outputs.clear()
        result = self.run_task('Create an innovative solution for reducing plastic waste in oceans.', 'creative_task')
        self.assertEqual(result.get_data('system_type'), 'slow')
        self.assertIsNotNone(result.get_data('output'))

    def test_system_switching(self):
        """Test the system's ability to switch between fast and slow thinking.
        
        Test cases:
        1. Initially simple but requiring deeper analysis
        2. Complex question with simple sub-tasks
        3. Error handling
        4. Confidence threshold boundary cases
        5. System interruption and recovery
        """
        # Case 1: Question requiring deeper analysis
        result = self.run_task('What is 2+2 and explain its significance in mathematical theory.', 'deeper_analysis')
        self.assertEqual(result.get_data('system_type'), 'slow')
        self.assertIn('4', result.get_data('output'))
        
        # Case 2: Complex question with simple sub-tasks
        self.stream_outputs.clear()
        result = self.run_task('Calculate the total cost: 3 items at $5 each, with 10% discount', 'complex_question')
        self.assertEqual(result.get_data('system_type'), 'fast')
        self.assertIn('13.5', result.get_data('output'))
        
        # Case 3: Error handling - empty input
        self.stream_outputs.clear()
        with self.assertRaises(ValueError):
            self.run_task('', 'error_handling')
            
        # Case 4: Error handling - very long input
        self.stream_outputs.clear()
        with self.assertRaises(ValueError):
            self.run_task('A' * 10000, 'error_handling')  # Very long input
            
        # Case 5: Confidence threshold boundary
        self.stream_outputs.clear()
        result = self.run_task('What is the 50th element in the periodic table?', 'confidence_boundary')
        confidence = result.get_data('confidence')
        self.assertTrue(0.6 <= confidence <= 0.8)  # Boundary case
        
        # Case 6: System interruption and recovery
        self.stream_outputs.clear()
        result = self.run_task('Analyze climate change impact but stop halfway', 'system_interruption')
        self.assertTrue(any(output.get('type') == 'interrupted' 
                          for output in self.stream_outputs))
        
    def test_concurrent_processing(self):
        """Test the agent's ability to handle concurrent requests.
        
        Test cases:
        1. Multiple fast thinking tasks
        2. Multiple slow thinking tasks
        3. Mix of fast and slow thinking tasks
        """
        import threading
        import queue
        
        results_queue = queue.Queue()
        
        def run_task(input_text: str, task_type: str):
            result = self.run_task(input_text, task_type)
            results_queue.put(result)
        
        # Case 1: Multiple fast thinking tasks
        fast_tasks = [
            ('What is 3 + 5?', 'fast_calculation'),
            ('What is the capital of Japan?', 'common_knowledge'),
            ('Is water wet?', 'pattern_matching')
        ]
        threads = []
        for task in fast_tasks:
            thread = threading.Thread(target=run_task, args=task)
            thread.start()
            threads.append(thread)
        
        for thread in threads:
            thread.join()
        
        while not results_queue.empty():
            result = results_queue.get()
            self.assertEqual(result.get_data('system_type'), 'fast')
            
        # Case 2: Mix of fast and slow thinking tasks
        mixed_tasks = [
            ('What is 7 * 8?', 'fast_calculation'),  # Fast
            ('Explain quantum entanglement', 'complex_analysis'),  # Slow
            ('Hello!', 'pattern_matching'),  # Fast
            ('Design a sustainable city', 'creative_task')  # Slow
        ]
        
        results_queue = queue.Queue()  # Clear queue
        threads = []
        for task in mixed_tasks:
            thread = threading.Thread(target=run_task, args=task)
            thread.start()
            threads.append(thread)
        
        for thread in threads:
            thread.join()
        
        fast_count = slow_count = 0
        while not results_queue.empty():
            result = results_queue.get()
            if result.get_data('system_type') == 'fast':
                fast_count += 1
            else:
                slow_count += 1
        
        self.assertEqual(fast_count, 2)
        self.assertEqual(slow_count, 2)

if __name__ == '__main__':
    unittest.main()
