from __future__ import annotations

import json
import logging
from typing import Any, Dict

from config.settings import settings

logger = logging.getLogger(__name__)


def _build_llm(model_name: str):
    """Create Gemini chat model lazily.

    Import is inside function so project still runs in heuristic mode
    when Gemini dependencies are not installed.
    """
    if not settings.google_api_key:
        return None

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(model=model_name, google_api_key=settings.google_api_key, temperature=0)
    except Exception as exc:
        logger.warning("Gemini client unavailable, falling back to deterministic mode: %s", exc)
        return None


def plan_with_gemini(payload: Dict[str, Any], model_name: str) -> Dict[str, Any] | None:
    llm = _build_llm(model_name)
    if llm is None:
        return None

    prompt = (
        "You are the Planning Agent for a campus HVAC BMS. "
        "Return strict JSON with keys: summary, required_state_fields, objective_weights. "
        "Keep required_state_fields as a list of telemetry field names only. "
        f"Input payload: {json.dumps(payload)}"
    )

    try:
        raw = llm.invoke(prompt).content
        if isinstance(raw, list):
            raw = "".join(str(x) for x in raw)
        raw = str(raw).strip().replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
    except Exception as exc:
        logger.warning("Gemini planning call failed, using deterministic fallback: %s", exc)
        return None
