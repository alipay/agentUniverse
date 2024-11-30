from enum import Enum
from dataclasses import dataclass
from typing import Any, Literal, Optional, Dict, TypedDict
from agentuniverse.base.common.constants import AgentKeys

class DualSystemKeys(str, Enum):
    """Keys specific to dual system thinking."""
    SYSTEM_TYPE = 'system_type'
    CONFIDENCE = 'confidence'
    THOUGHT = 'thought'
    RESPONSE = 'response'
    COMPLEXITY = 'complexity'

class SystemType(str, Enum):
    """System types for dual system thinking."""
    FAST = 'fast_thinking'
    SLOW = 'slow_thinking'

class ThinkingState(str, Enum):
    """States in the thinking process."""
    EVALUATING = 'evaluating'
    FAST_PROCESSING = 'fast_processing'
    SLOW_PROCESSING = 'slow_processing'
    COMPLETED = 'completed'

class ComplexityLevel(str, Enum):
    """Complexity levels for input evaluation."""
    SIMPLE = 'simple'
    MODERATE = 'moderate'
    COMPLEX = 'complex'

class ComplexityFactor(str, Enum):
    """Factors affecting input complexity."""
    TEXT_LENGTH = 'text_length'
    QUESTION_TYPE = 'question_type'
    KEYWORD_COMPLEXITY = 'keyword_complexity'
    CONTEXT_DEPENDENCY = 'context_dependency'

@dataclass
class ThinkingResult:
    """Data class for thinking results."""
    system_type: SystemType
    output: Any
    confidence: float
    thought: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            AgentKeys.OUTPUT: self.output,
            DualSystemKeys.SYSTEM_TYPE: self.system_type,
            DualSystemKeys.CONFIDENCE: self.confidence,
            DualSystemKeys.THOUGHT: self.thought
        }

@dataclass
class ComplexityScore:
    """Data class for complexity evaluation results."""
    text_length_score: float
    question_type_score: float
    keyword_complexity_score: float
    context_dependency_score: float
    overall_score: float
    level: ComplexityLevel

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            ComplexityFactor.TEXT_LENGTH: self.text_length_score,
            ComplexityFactor.QUESTION_TYPE: self.question_type_score,
            ComplexityFactor.KEYWORD_COMPLEXITY: self.keyword_complexity_score,
            ComplexityFactor.CONTEXT_DEPENDENCY: self.context_dependency_score,
            'overall_score': self.overall_score,
            'level': self.level
        }
