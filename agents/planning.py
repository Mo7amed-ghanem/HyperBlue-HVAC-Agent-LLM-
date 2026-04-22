from __future__ import annotations

import logging

from config.settings import settings
from llm.gemini_client import plan_with_gemini
from schemas import GoalRequest, PlannerTask

logger = logging.getLogger(__name__)


DEFAULT_FIELDS = ["indoor_temp_per_room", "outdoor_temp", "co2_levels", "occupancy", "hvac_status"]


def planning_agent(goal: GoalRequest) -> PlannerTask:
    logger.info("Planning agent: building orchestration task from goals")

    llm_payload = {
        "goal": goal.model_dump(),
        "note": "Create a concise orchestration plan for HVAC multi-objective optimization.",
    }
    llm_result = plan_with_gemini(llm_payload, model_name=settings.planner_model)

    if llm_result:
        try:
            return PlannerTask.model_validate(llm_result)
        except Exception as exc:
            logger.warning("Gemini output failed schema validation, fallback deterministic plan: %s", exc)

    summary = "Coordinate HVAC optimization across requested zones with weighted multi-objective score"
    return PlannerTask(summary=summary, required_state_fields=DEFAULT_FIELDS, objective_weights=goal.weights)
