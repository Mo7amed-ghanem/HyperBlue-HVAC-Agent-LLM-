from __future__ import annotations

import logging

from schemas import HvacTargets, SafetyDecision, UserRole

logger = logging.getLogger(__name__)


MIN_TEMP_C = 20.0
MAX_TEMP_C = 26.0


ALLOWED_ZONES_FOR_STAFF = {"ENGR-101", "LIB-204"}


def safety_policy_agent(role: UserRole, proposal: HvacTargets) -> SafetyDecision:
    logger.info("Safety/policy agent: enforcing RBAC and physical constraints")

    if role == UserRole.STUDENT:
        return SafetyDecision(approved=False, reason="Student role is read-only")

    sanitized = proposal.model_copy(deep=True)
    modifications = []

    if role == UserRole.STAFF:
        unauthorized = [z for z in sanitized.zone_targets_c if z not in ALLOWED_ZONES_FOR_STAFF]
        if unauthorized:
            for z in unauthorized:
                sanitized.zone_targets_c.pop(z)
            modifications.append(f"Removed unauthorized zones for Staff: {unauthorized}")

    for zone, tgt in list(sanitized.zone_targets_c.items()):
        clamped = min(MAX_TEMP_C, max(MIN_TEMP_C, tgt))
        if clamped != tgt:
            sanitized.zone_targets_c[zone] = clamped
            modifications.append(f"Clamped {zone} target from {tgt}C to {clamped}C")

    sanitized.fan_speed_pct = min(95, max(20, sanitized.fan_speed_pct))
    sanitized.fresh_air_pct = min(80, max(10, sanitized.fresh_air_pct))

    reason = "Approved" if not modifications else "Approved with safety/policy modifications"
    return SafetyDecision(approved=True, reason=reason, sanitized_targets=sanitized)
