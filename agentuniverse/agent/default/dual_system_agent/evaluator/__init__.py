#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Evaluator package initialization."""

from agentuniverse.agent.default.dual_system_agent.evaluator.evaluator_manager import EvaluatorManager
from agentuniverse.agent.default.dual_system_agent.complexity_evaluator import DefaultComplexityEvaluator

# Register default evaluator
EvaluatorManager().register("default_complexity_evaluator", DefaultComplexityEvaluator)
EvaluatorManager().set_default("default_complexity_evaluator")
