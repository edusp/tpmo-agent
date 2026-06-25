"""
LLM configuration for CrewAI agents.
Returns a configured LLM instance based on available environment variables.
"""

import os
from django.conf import settings


def get_llm():
    """
    Return a crewai-compatible LLM string or object.
    Reads model from settings; defaults to gpt-4o-mini.
    """
    model = getattr(settings, "TPMO_LLM_MODEL", "gpt-4o-mini")
    return model
