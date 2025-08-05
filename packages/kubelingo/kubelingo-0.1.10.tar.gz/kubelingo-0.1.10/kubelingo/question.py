"""
Question schema for unified live exercise mode.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class ValidationStep:
    """
    A single validation step: run `cmd` and apply `matcher` to its output.
    matcher could specify JSONPath, regex, substring, etc.
    """
    cmd: str
    matcher: Dict[str, Any]

@dataclass
class Question:
    """
    Canonical question object for unified shell exercises and quizzes.
    """
    id: str                           # unique identifier, e.g. 'module::index'
    prompt: str                       # text shown to the user
    type: str = ''                   # question type, e.g. 'command', 'live_k8s', etc.
    
    # Unified shell experience fields
    pre_shell_cmds: List[str] = field(default_factory=list)   # commands to prepare sandbox
    initial_files: Dict[str, str] = field(default_factory=dict)  # file path → content to seed workspace
    validation_steps: List[ValidationStep] = field(default_factory=list)  # steps to run after shell exit
    validator: Optional[Dict[str, Any]] = None  # For AI-based validation

    # Metadata
    explanation: Optional[str] = None
    categories: List[str] = field(default_factory=list)
    difficulty: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

