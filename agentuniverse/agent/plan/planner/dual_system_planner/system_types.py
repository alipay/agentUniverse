# !/usr/bin/env python3
# -*- coding:utf-8 -*-

from enum import Enum, auto

class SystemType(Enum):
    """System types for dual system thinking."""
    FAST = auto()  # System 1
    SLOW = auto()  # System 2

class ThinkingState(Enum):
    """Thinking states in the dual system process."""
    EVALUATING = auto()    # Initial evaluation
    FAST_THINKING = auto() # System 1 processing
    SLOW_THINKING = auto() # System 2 processing
    COMPLETED = auto()     # Processing complete
