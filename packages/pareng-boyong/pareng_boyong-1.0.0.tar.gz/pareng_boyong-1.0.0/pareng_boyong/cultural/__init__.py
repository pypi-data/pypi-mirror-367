"""
Filipino Cultural Integration Module for Pareng Boyong.

This module provides Filipino cultural context, language processing,
and culturally-aware responses for the AI agent system.

Features:
- Filipino/Tagalog language support
- Cultural context awareness (bayanihan, kapamilya, etc.)
- Respectful communication patterns (po/opo)
- Local business and social practices
- Philippine geography and time zone awareness
"""

from .identity import FilipinoIdentity
from .language import LanguageProcessor
from .greetings import (
    get_random_greeting,
    get_time_appropriate_greeting,
    get_cultural_response
)
from .values import FilipinoValues

__all__ = [
    "FilipinoIdentity",
    "LanguageProcessor", 
    "get_random_greeting",
    "get_time_appropriate_greeting",
    "get_cultural_response",
    "FilipinoValues",
]