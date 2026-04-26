"""
transaction_engine — Deterministic financial query engine for Orion voice agent.

Drop-in replacement for the Groq/OpenAI LLM. No hallucination. No network calls.

Usage in agent.py:
    from transaction_engine import TransactionLLM
    llm_model = TransactionLLM()

Public API:
    TransactionLLM   — LiveKit LLM-compatible class (main integration point)
    QueryEngine      — Direct query access if needed
    startup_summary  — Returns the financial greeting string
"""

from .llm_adapter import TransactionLLM
from .query_engine import QueryEngine


def startup_summary() -> str:
    """
    Convenience wrapper: returns the financial greeting string.
    Called in agent.py to replace the generic 'Hey I'm Orion' greeting.
    """
    return QueryEngine().startup_summary()


__all__ = ["TransactionLLM", "QueryEngine", "startup_summary"]
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
