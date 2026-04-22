from __future__ import annotations

import json
import logging
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from environment.simulator import MockBmsEnvironment
from graph.bms_graph import build_bms_graph
from schemas import GoalRequest, UserRole

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)


def run_case(label: str, env: MockBmsEnvironment, goal: GoalRequest, role: UserRole):
    print(f"\n===== {label} =====")
    app = build_bms_graph(env)
    result = app.invoke({"goal": goal, "user_role": role})
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    base_goal = GoalRequest(
        improve_comfort=True,
        reduce_co2=True,
        optimize_energy=True,
        zone_scope=["ENGR-101", "LIB-204", "CHEM-110"],
        weights={"comfort": 0.5, "energy": 0.25, "air_quality": 0.25},
    )

    # 1) Normal operation
    env_normal = MockBmsEnvironment()
    run_case("Normal operation (Staff)", env_normal, base_goal, UserRole.STAFF)

    # 2) Constraint violation case (aggressive comfort, high overrides/clamping expected)
    env_violation = MockBmsEnvironment()
    env_violation.rooms["ENGR-101"]["temp"] = 34.5
    env_violation.rooms["CHEM-110"]["co2"] = 1650
    run_case("Constraint violation stress (Admin)", env_violation, deepcopy(base_goal), UserRole.ADMIN)

    # 3) Role restriction
    env_student = MockBmsEnvironment()
    run_case("Role-based restriction (Student)", env_student, deepcopy(base_goal), UserRole.STUDENT)

    # 4) Tool offline failure scenario
    env_tool_offline = MockBmsEnvironment()
    env_tool_offline.set_tool_health("get_co2_level", False)
    env_tool_offline.set_tool_health("apply_mpc_targets", False)
    run_case("Tool offline diagnostics", env_tool_offline, deepcopy(base_goal), UserRole.ADMIN)
