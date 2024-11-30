#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Base evaluator interface for complexity evaluation."""

from abc import ABC, abstractmethod
from agentuniverse.agent.default.dual_system_agent.constants import ComplexityScore

class BaseEvaluator(ABC):
    """Base interface for complexity evaluators."""
    
    @abstractmethod
    def evaluate(self, text: str) -> ComplexityScore:
        """Evaluate input complexity.
        
        Args:
            text: Input text to evaluate
            
        Returns:
            ComplexityScore: Complexity evaluation results
        """
        pass

    @abstractmethod
    def evaluate_text_length(self, text: str) -> float:
        """Evaluate complexity based on text length.
        
        Args:
            text: Input text to evaluate
            
        Returns:
            float: Score between 0 and 1, where higher means more complex
        """
        pass

    @abstractmethod
    def evaluate_question_type(self, text: str) -> float:
        """Evaluate complexity based on question type.
        
        Args:
            text: Input text to evaluate
            
        Returns:
            float: Score between 0 and 1, where higher means more complex
        """
        pass

    @abstractmethod
    def evaluate_keyword_complexity(self, text: str) -> float:
        """Evaluate complexity based on keyword analysis.
        
        Args:
            text: Input text to evaluate
            
        Returns:
            float: Score between 0 and 1, where higher means more complex
        """
        pass

    @abstractmethod
    def evaluate_context_dependency(self, text: str) -> float:
        """Evaluate complexity based on context dependency.
        
        Args:
            text: Input text to evaluate
            
        Returns:
            float: Score between 0 and 1, where higher means more complex
        """
        pass
