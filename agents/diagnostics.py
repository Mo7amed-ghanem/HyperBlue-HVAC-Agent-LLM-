from __future__ import annotations

import logging
from typing import Iterable, List

from schemas import DiagnosticIssue, DiagnosticsReport, EnvironmentState, ErrorType, GoalRequest, HvacTargets

logger = logging.getLogger(__name__)


def feasibility_diagnostics_agent(
    goal: GoalRequest,
    env_state: EnvironmentState,
    proposal: HvacTargets,
    unavailable_tools: Iterable[str],
) -> DiagnosticsReport:
    logger.info("Diagnostics agent: validating proposal and prerequisites")
    issues: List[DiagnosticIssue] = []

    if unavailable_tools:
        issues.append(
            DiagnosticIssue(
                error_type=ErrorType.TOOL_UNAVAILABLE,
                detail=f"Unavailable tool integrations: {', '.join(unavailable_tools)}",
            )
        )

    for room in env_state.rooms:
        if room.indoor_temp_c is None or room.co2_ppm is None:
            issues.append(
                DiagnosticIssue(
                    error_type=ErrorType.DATA_MISSING,
                    detail=f"Missing data for room {room.room_id}",
                )
            )

    if goal.optimize_energy and goal.improve_comfort and any(c > 1400 for c in [r.co2_ppm for r in env_state.rooms]):
        issues.append(
            DiagnosticIssue(
                error_type=ErrorType.GOAL_CONFLICT,
                detail="High CO2 with aggressive energy savings may reduce ventilation quality",
            )
        )

    for zone, target in proposal.zone_targets_c.items():
        if not 10 <= target <= 35:
            issues.append(
                DiagnosticIssue(
                    error_type=ErrorType.INVALID_RANGE,
                    detail=f"Target {target}C for {zone} outside expected engineering range",
                )
            )

    return DiagnosticsReport(ok=len(issues) == 0, issues=issues)
