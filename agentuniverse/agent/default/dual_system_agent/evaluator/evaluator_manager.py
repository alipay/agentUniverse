#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Evaluator manager for managing different complexity evaluators."""

from typing import Dict, Type
from agentuniverse.base.annotation.singleton import singleton
from agentuniverse.agent.default.dual_system_agent.evaluator.base_evaluator import BaseEvaluator
from typing import Optional

@singleton
class EvaluatorManager:
    """Manager class for complexity evaluators."""
    
    def __init__(self) -> None:
        """Initialize evaluator manager."""
        self._evaluators: Dict[str, Type[BaseEvaluator]] = {}
        self._default_evaluator: Optional[str] = None
        
    def register(self, name: str, evaluator_class: Type[BaseEvaluator]) -> None:
        """Register an evaluator.
        
        Args:
            name: Name of the evaluator
            evaluator_class: Evaluator class to register
        """
        self._evaluators[name] = evaluator_class
        if self._default_evaluator is None:
            self._default_evaluator = name
            
    def set_default(self, name: str) -> None:
        """Set the default evaluator.
        
        Args:
            name: Name of the evaluator to set as default
        """
        if name is None:
            self._default_evaluator = None
        if name not in self._evaluators:
            raise ValueError(f"Evaluator {name} not found")
        self._default_evaluator = name
        
    def get_evaluator(self, name: Optional[str] = None) -> BaseEvaluator:
        """Get an evaluator instance.
        
        Args:
            name: Name of the evaluator to get, if None returns default
            
        Returns:
            BaseEvaluator: An instance of the requested evaluator
        """
        evaluator_name = name or self._default_evaluator
        if evaluator_name not in self._evaluators:
            raise ValueError(f"Evaluator {evaluator_name} not found")
        return self._evaluators[evaluator_name]()
