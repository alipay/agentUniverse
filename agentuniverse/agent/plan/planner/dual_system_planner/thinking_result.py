# !/usr/bin/env python3
# -*- coding:utf-8 -*-

from dataclasses import dataclass
from typing import Any, Optional

from .system_types import SystemType

@dataclass
class ThinkingResult:
    """Result object for dual system thinking."""
    system_type: SystemType
    output: Any
    confidence: float
    thought: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary format."""
        return {
            'system_type': self.system_type.name.lower(),
            'result': self.output,
            'confidence': self.confidence,
            'thought': self.thought
        }
