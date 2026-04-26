"""
llm_adapter.py — Drop-in LiveKit LLM replacement backed by the transaction engine.

Drop-in usage in agent.py:
    from transaction_engine import TransactionLLM
    llm_model = TransactionLLM()

The voice pipeline (STT → LLM → TTS) stays identical.
No network calls. Zero hallucination.
"""

import logging
from typing import Any

from livekit.agents import llm
from livekit.agents.llm import ChatChunk, ChatContext, ChoiceDelta
from livekit.agents.llm.llm import DEFAULT_API_CONNECT_OPTIONS, APIConnectOptions
from livekit.agents.utils import shortuuid

from .context_manager import ContextManager
from .intent_engine import parse_intent
from .query_engine import QueryEngine
from . import insight_engine as ie
from . import report_engine as _re
from . import response_formatter as rf
from .whatsapp_sender import send_whatsapp

logger = logging.getLogger("transaction-llm")

# Shared engine and context — one instance per agent process
_engine: QueryEngine | None = None
_context: ContextManager = ContextManager()


def _get_engine() -> QueryEngine:
    global _engine
    if _engine is None:
        _engine = QueryEngine()
        logger.info(f"TransactionEngine loaded {len(_engine.transactions)} transactions")
    return _engine


def _extract_user_text(chat_ctx: ChatContext) -> str:
    """Pull the last user message text from ChatContext."""
    for item in reversed(chat_ctx.items):
        if hasattr(item, "role") and item.role == "user":
            text = item.text_content
            return text if text else ""
    return ""


def _dispatch(user_text: str, engine: QueryEngine, ctx: ContextManager) -> str:
    """
    Full pipeline: user text → intent → query → formatted response string.
    Returns a plain string ready for TTS.
    """
    parsed = parse_intent(user_text)
    intent = parsed["intent"]
    lang = parsed.get("lang", "en")

    # Context-aware follow-up: "unse", "unka", etc. — reuse last person/category
    if intent == "unknown" and ctx.is_followup(user_text):
        if ctx.last_person and ctx.last_intent == "get_transactions_by_person":
            intent = "get_transactions_by_person"
            parsed["params"] = {"name": ctx.last_person}
        elif ctx.last_category and ctx.last_intent == "get_category_spend":
            intent = "get_category_spend"
            parsed["params"] = {"category": ctx.last_category, "date_range": None}

    if intent == "unknown":
        return rf.format_unknown(parsed.get("message"), lang=lang)

    params = ctx.resolve(intent, parsed.get("params", {}))

    # ── Route to query/insight function ──────────────────────────────────────
    result: dict = {}
    response: str = ""

    if intent == "get_total_received":
        date_input = params.get("date_range") or params.get("date")
        result = engine.get_total_received(date_input)
        response = rf.format_total_received(result, lang=lang)

    elif intent == "get_total_spent":
        date_input = params.get("date_range") or params.get("date")
        result = engine.get_total_spent(date_input)
        response = rf.format_total_spent(result, lang=lang)

    elif intent == "get_last_transaction":
        result = engine.get_last_transaction()
        response = rf.format_last_transaction(result, lang=lang)

    elif intent == "get_transactions_by_person":
        name = params.get("name") or ""
        result = engine.get_transactions_by_person(name)
        response = rf.format_person_query(result, lang=lang)

    elif intent == "check_payment":
        amount = params.get("amount", 0) or 0
        date_input = params.get("date")
        result = engine.check_payment(float(amount), date_input)
        response = rf.format_check_payment(result, float(amount), lang=lang)

    elif intent == "get_category_spend":
        category = params.get("category") or "other"
        date_range = params.get("date_range")
        result = engine.get_category_spend(category, date_range)
        response = rf.format_category_spend(result, lang=lang)

    elif intent == "get_top_category":
        date_range = params.get("date_range")
        result = ie.get_top_category(engine.transactions, date_range)
        response = rf.format_top_category(result, lang=lang)

    elif intent == "get_top_person":
        txn_type = params.get("type", "credit")
        result = ie.get_top_person(engine.transactions, txn_type)
        response = rf.format_top_person(result, lang=lang)

    elif intent == "detect_anomalies":
        anomalies = ie.detect_anomalies(engine.transactions)
        result = {"anomalies": anomalies}
        response = rf.format_anomalies(anomalies, lang=lang)

    elif intent == "get_spending_trend":
        trend = ie.get_spending_trend(engine.transactions)
        result = {"trend": trend}
        response = rf.format_spending_trend(trend, lang=lang)

    elif intent == "send_whatsapp_report":
        from datetime import date, timedelta
        period = params.get("period", "this_week")
        today = date.today()
        if period == "last_week":
            start = today - timedelta(days=today.weekday() + 7)
            end = start + timedelta(days=6)
        elif period == "this_month":
            start = today.replace(day=1)
            end = today
        else:  # this_week
            start = today - timedelta(days=today.weekday())
            end = today
        report = _re.generate_report(engine.transactions, start, end)
        msg_text = _re.build_whatsapp_message(report)
        _re.generate_pdf(report)  # saved locally to data/reports/
        success = send_whatsapp(msg_text)
        response = rf.format_whatsapp_sent(success, period, lang=lang)

    else:
        response = rf.format_unknown(lang=lang)

    # Update context for follow-up resolution
    ctx.update(intent, params, result)
    logger.debug(f"intent={intent} params={params} → {response[:80]}")
    return response


# ─── LiveKit LLM Stream ───────────────────────────────────────────────────────

class _TransactionStream(llm.LLMStream):
    def __init__(
        self,
        llm_instance: "TransactionLLM",
        *,
        chat_ctx: ChatContext,
        conn_options: APIConnectOptions,
    ) -> None:
        super().__init__(
            llm_instance,
            chat_ctx=chat_ctx,
            tools=[],
            conn_options=conn_options,
        )
        self._tx_llm = llm_instance

    async def _run(self) -> None:
        user_text = _extract_user_text(self._chat_ctx)
        if not user_text.strip():
            response = "I didn't catch that — could you repeat?"
        else:
            try:
                response = _dispatch(user_text, self._tx_llm.engine, self._tx_llm.ctx)
            except Exception as e:
                logger.error(f"TransactionEngine error: {e}", exc_info=True)
                response = "Sorry, I ran into an issue looking that up. Try again?"

        chunk = ChatChunk(
            id=shortuuid("txn_chunk_"),
            delta=ChoiceDelta(role="assistant", content=response),
        )
        self._event_ch.send_nowait(chunk)


# ─── LiveKit LLM ─────────────────────────────────────────────────────────────

class TransactionLLM(llm.LLM):
    """
    Drop-in replacement for openai.LLM().
    Answers financial queries deterministically from local transaction data.
    """

    def __init__(self) -> None:
        super().__init__()
        self.engine: QueryEngine = _get_engine()
        self.ctx: ContextManager = ContextManager()
        logger.info("TransactionLLM ready")

    @property
    def model(self) -> str:
        return "transaction-engine-v1"

    @property
    def provider(self) -> str:
        return "local"

    def chat(
        self,
        *,
        chat_ctx: ChatContext,
        tools: Any = None,
        conn_options: APIConnectOptions = DEFAULT_API_CONNECT_OPTIONS,
        parallel_tool_calls: Any = None,
        tool_choice: Any = None,
        extra_kwargs: Any = None,
    ) -> _TransactionStream:
        return _TransactionStream(
            self,
            chat_ctx=chat_ctx,
            conn_options=conn_options,
        )
 
 
 
