"""
context_manager.py — Session-scoped memory for conversational follow-ups.

Stores the last turn's person, category, intent, and result so that
follow-up queries like "unse pichli baar?" or "is mahine?" resolve correctly.

ContextManager is stateful and lives for the duration of one voice session.
"""

from typing import Optional


class ContextManager:
    """Holds memory across turns within a single voice session."""

    def __init__(self) -> None:
        self.last_person: Optional[str] = None       # canonical name from last person query
        self.last_category: Optional[str] = None     # category from last category query
        self.last_intent: Optional[str] = None       # last resolved intent name
        self.last_result: Optional[dict] = None      # last raw result dict
        self.last_params: Optional[dict] = None      # params used in last query

    def update(self, intent: str, params: dict, result: dict) -> None:
        """Call after every successful query to save context."""
        self.last_intent = intent
        self.last_params = params
        self.last_result = result

        # Persist person
        if intent == "get_transactions_by_person":
            canonical = result.get("canonical")
            if canonical:
                self.last_person = canonical

        # Persist category
        if intent == "get_category_spend":
            cat = params.get("category") or result.get("category")
            if cat:
                self.last_category = cat

    def resolve(self, intent: str, params: dict) -> dict:
        """
        Fill in missing params from context.

        Examples:
          - "unse kitna aaya?" with intent=get_transactions_by_person, params={name: None}
            → fills name from last_person
          - "is mahine?" with intent=get_category_spend, params={category: None}
            → fills category from last_category
        """
        resolved = dict(params)

        if intent == "get_transactions_by_person":
            if not resolved.get("name") and self.last_person:
                resolved["name"] = self.last_person

        if intent == "get_category_spend":
            if not resolved.get("category") and self.last_category:
                resolved["category"] = self.last_category

        return resolved

    def is_followup(self, text: str) -> bool:
        """
        Detect if the user is asking a follow-up about the previous subject.
        Trigger words: 'unse', 'unka', 'woh', 'same', 'uska', 'us'
        """
        t = text.lower()
        followup_words = {"unse", "unka", "unki", "unke", "woh", "uska", "uski", "us", "same"}
        return any(w in t.split() for w in followup_words)

    def clear(self) -> None:
        """Reset all context (e.g. on session end)."""
        self.last_person = None
        self.last_category = None
        self.last_intent = None
        self.last_result = None
        self.last_params = None

    def __repr__(self) -> str:
        return (
            f"ContextManager("
            f"person={self.last_person!r}, "
            f"category={self.last_category!r}, "
            f"intent={self.last_intent!r})"
        )
 
 
 
 
