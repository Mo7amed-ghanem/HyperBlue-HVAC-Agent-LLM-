from __future__ import annotations

import logging

from schemas import GoalRequest, PlannerTask

logger = logging.getLogger(__name__)


def planning_agent(goal: GoalRequest) -> PlannerTask:
    logger.info("Planning agent: building orchestration task from goals")
    fields = ["indoor_temp_per_room", "outdoor_temp", "co2_levels", "occupancy", "hvac_status"]
    summary = "Coordinate HVAC optimization across requested zones with weighted multi-objective score"
    return PlannerTask(summary=summary, required_state_fields=fields, objective_weights=goal.weights)
