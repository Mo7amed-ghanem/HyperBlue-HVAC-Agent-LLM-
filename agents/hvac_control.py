from __future__ import annotations

import logging
from typing import Dict

from schemas import EnvironmentState, GoalRequest, HvacTargets

logger = logging.getLogger(__name__)


IDEAL_TEMP = 23.5
MAX_CO2 = 1000


def _comfort_score(temp: float) -> float:
    return max(0.0, 1 - abs(temp - IDEAL_TEMP) / 8)


def _energy_penalty(temp_target: float, outdoor_temp: float) -> float:
    return min(1.0, abs(temp_target - outdoor_temp) / 18)


def _air_quality_score(co2: int) -> float:
    return max(0.0, 1 - max(0, co2 - 600) / 1200)


def _normalized_weights(goal: GoalRequest) -> Dict[str, float]:
    total = max(1e-9, sum(goal.weights.values()))
    return {k: v / total for k, v in goal.weights.items()}


def hvac_control_agent(goal: GoalRequest, env_state: EnvironmentState) -> HvacTargets:
    logger.info("HVAC control agent: computing high-level targets")

    w = _normalized_weights(goal)
    targets: Dict[str, float] = {}
    co2_values = []

    for room in env_state.rooms:
        if room.indoor_temp_c is None or room.co2_ppm is None:
            continue

        co2_values.append(room.co2_ppm)
        comfort = _comfort_score(room.indoor_temp_c)
        air_quality = _air_quality_score(room.co2_ppm)

        proposed = room.indoor_temp_c
        if goal.improve_comfort:
            proposed += -1.5 if room.indoor_temp_c > IDEAL_TEMP else 0.5
        if goal.optimize_energy and env_state.outdoor_temp_c < room.indoor_temp_c:
            proposed += 0.4

        energy = _energy_penalty(proposed, env_state.outdoor_temp_c)
        j = w["comfort"] * comfort + w["energy"] * (1 - energy) + w["air_quality"] * air_quality

        if j < 0.45 and goal.reduce_co2:
            proposed -= 0.3

        targets[room.room_id] = round(proposed, 2)

    avg_co2 = sum(co2_values) / len(co2_values) if co2_values else 600
    fan_speed_pct = 75 if avg_co2 > MAX_CO2 else 55
    fresh_air_pct = 40 if avg_co2 > MAX_CO2 else 22

    rationale = "Computed from normalized weighted objective J=w1*comfort+w2*energy+w3*air_quality"
    return HvacTargets(
        zone_targets_c=targets,
        fan_speed_pct=fan_speed_pct,
        fresh_air_pct=fresh_air_pct,
        rationale=rationale,
    )
