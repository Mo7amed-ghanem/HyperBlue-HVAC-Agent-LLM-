from __future__ import annotations

import logging

from schemas import EnvironmentState, HvacTargets, OversightResult

logger = logging.getLogger(__name__)


def mpc_oversight_agent(env_state: EnvironmentState, proposal: HvacTargets) -> OversightResult:
    """Simplified deterministic MPC-like supervisor.

    - Smooths abrupt setpoint jumps (<= 1.2C per control cycle)
    - Soft-limits fan and fresh-air requests
    """

    logger.info("MPC oversight: applying smoothing and soft constraints")
    room_now = {r.room_id: r.indoor_temp_c for r in env_state.rooms}
    adjusted = proposal.model_copy(deep=True)
    overrides = []

    for zone, tgt in proposal.zone_targets_c.items():
        now = room_now.get(zone)
        if now is None:
            continue
        delta = tgt - now
        if abs(delta) > 1.2:
            clipped = round(now + (1.2 if delta > 0 else -1.2), 2)
            adjusted.zone_targets_c[zone] = clipped
            overrides.append(f"Smoothed {zone} from {tgt}C to {clipped}C")

    if adjusted.fan_speed_pct > 85:
        overrides.append("Fan speed soft-capped at 85%")
        adjusted.fan_speed_pct = 85
    if adjusted.fresh_air_pct > 60:
        overrides.append("Fresh air soft-capped at 60%")
        adjusted.fresh_air_pct = 60

    return OversightResult(adjusted_targets=adjusted, overrides_applied=overrides)
