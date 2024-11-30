from enum import Enum
from dataclasses import dataclass
from typing import Any, Literal, Optional, Dict, TypedDict
from agentuniverse.common.constants import AgentKeys

class DualSystemKeys(str, Enum):
    """Keys specific to dual system thinking."""
    SYSTEM_TYPE = 'system_type'
    CONFIDENCE = 'confidence'
    THOUGHT = 'thought'
    RESPONSE = 'response'

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

