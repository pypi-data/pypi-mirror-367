"""
Agent loops for agent
"""

# Import the loops to register them
from . import anthropic
from . import openai
from . import uitars
from . import omniparser

__all__ = ["anthropic", "openai", "uitars", "omniparser"]
