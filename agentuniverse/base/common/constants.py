from enum import Enum
from dataclasses import dataclass
from typing import Any, Literal, Optional, TypedDict, Dict

class AgentKeys(str, Enum):
    """Common keys used across different agents."""
    INPUT = 'input'
    OUTPUT = 'output'
    CONFIDENCE = 'confidence'
    THOUGHT = 'thought'
    SYSTEM_TYPE = 'system_type'
    STREAM_CALLBACK = 'stream_callback'
    PROMPT_VERSION = 'prompt_version'