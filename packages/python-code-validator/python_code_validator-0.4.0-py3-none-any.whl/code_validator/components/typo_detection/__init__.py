"""Smart typo detection system for Python Code Validator.

This package provides intelligent typo detection and suggestion capabilities
for validation rules. When a selector fails to find a target name, the system
analyzes similar names in the same scope and provides helpful suggestions.

Example:
    Instead of just "Required attribute 'self.speed' not found",
    users get "Did you mean 'self.speed' instead of 'self.sped'?"

Classes:
    TypoDetector: Main detector class for analyzing failed searches
    ScopeAnalyzer: Extracts names from specific AST scopes
    PythonStyleFormatter: Formats suggestions like Python 3.11+ errors
"""

from .detector import TypoDetector
from .formatters import PythonStyleFormatter
from .scope_analyzer import ScopeAnalyzer

__all__ = [
    "TypoDetector",
    "ScopeAnalyzer",
    "PythonStyleFormatter",
]
