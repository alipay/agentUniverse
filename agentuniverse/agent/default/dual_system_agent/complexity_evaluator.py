#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Default complexity evaluator implementation."""

import re
from typing import Set, List, Dict
from agentuniverse.agent.default.dual_system_agent.constants import (
    ComplexityScore, ComplexityLevel, ComplexityFactor
)
from agentuniverse.agent.default.dual_system_agent.evaluator.base_evaluator import BaseEvaluator

class DefaultComplexityEvaluator(BaseEvaluator):
    """Default implementation of complexity evaluator."""

    def __init__(self) -> None:
        """Initialize the evaluator with configuration."""
        # 简单问题的关键词集合
        self._simple_keywords: Set[str] = {
            '什么是', '定义', '解释', '加', '减', '乘', 
            'what is', 'define', 'explain', 'add', 'subtract', 'multiply'
        }
        
        # 复杂问题的关键词集合
        self._complex_keywords: Set[str] = {
            '为什么', '如何', '分析', '比较', '评估', '预测', '优化',
            'why', 'how', 'analyze', 'compare', 'evaluate', 'predict', 'optimize'
        }

        # 上下文依赖词集合
        self._context_keywords: Set[str] = {
            '这个', '那个', '它', '他们', '之前', '刚才',
            'this', 'that', 'it', 'they', 'previous', 'before'
        }

    def evaluate_text_length(self, text: str) -> float:
        """Evaluate complexity based on text length."""
        length = len(text)
        if length <= 10:
            return 0.2
        elif length <= 30:
            return 0.5
        elif length <= 100:
            return 0.8
        return 1.0

    def evaluate_question_type(self, text: str) -> float:
        """Evaluate complexity based on question type."""
        text = text.lower()
        
        # 检查简单关键词
        for keyword in self._simple_keywords:
            if keyword.lower() in text:
                return 0.3
                
        # 检查复杂关键词
        for keyword in self._complex_keywords:
            if keyword.lower() in text:
                return 0.8
                
        return 0.5  # 默认中等复杂度

    def evaluate_keyword_complexity(self, text: str) -> float:
        """Evaluate complexity based on keyword analysis."""
        words = set(re.split(r'\s+|[,.，。]', text.lower()))
        
        # 计算复杂词汇的比例
        complex_word_count = len([w for w in words if len(w) > 4])
        if not words:
            return 0.5
            
        return min(1.0, complex_word_count / len(words))

    def evaluate_context_dependency(self, text: str) -> float:
        """Evaluate complexity based on context dependency."""
        text = text.lower()
        context_keyword_count = sum(1 for keyword in self._context_keywords 
                                  if keyword.lower() in text)
        
        if context_keyword_count == 0:
            return 0.2
        elif context_keyword_count == 1:
            return 0.5
        elif context_keyword_count == 2:
            return 0.8
        return 1.0

    def evaluate(self, text: str) -> ComplexityScore:
        """Evaluate overall input complexity."""
        # 计算各维度分数
        text_length_score = self.evaluate_text_length(text)
        question_type_score = self.evaluate_question_type(text)
        keyword_complexity_score = self.evaluate_keyword_complexity(text)
        context_dependency_score = self.evaluate_context_dependency(text)
        
        # 计算总体分数（可以调整权重）
        weights = {
            'text_length': 0.2,
            'question_type': 0.3,
            'keyword_complexity': 0.3,
            'context_dependency': 0.2
        }
        
        overall_score = (
            text_length_score * weights['text_length'] +
            question_type_score * weights['question_type'] +
            keyword_complexity_score * weights['keyword_complexity'] +
            context_dependency_score * weights['context_dependency']
        )
        
        # 确定复杂度级别
        if overall_score < 0.4:
            level = ComplexityLevel.SIMPLE
        elif overall_score < 0.8:
            level = ComplexityLevel.MODERATE
        else:
            level = ComplexityLevel.COMPLEX
            
        return ComplexityScore(
            text_length_score=text_length_score,
            question_type_score=question_type_score,
            keyword_complexity_score=keyword_complexity_score,
            context_dependency_score=context_dependency_score,
            overall_score=overall_score,
            level=level
        )
