from __future__ import annotations

import logging
from typing import List

from environment.simulator import MockBmsEnvironment
from schemas import EnvironmentState, UserRole
from tools.bms_tools import BmsToolbox

logger = logging.getLogger(__name__)


REQUIRED_CONTEXT_TOOLS = ["get_room_state", "get_outdoor_weather", "get_occupancy", "get_co2_level"]


def context_state_agent(env: MockBmsEnvironment, role: UserRole) -> tuple[EnvironmentState, List[str]]:
    """Collects structured environment state and records offline dependencies."""
    logger.info("Context/state agent: collecting structured telemetry")
    tools = BmsToolbox(env, role.value)

    unavailable = [
        tool_name
        for tool_name in REQUIRED_CONTEXT_TOOLS
        if not tools.check_tool_status.invoke({"tool_name": tool_name})
    ]

    env_state = env.get_full_state()
    return env_state, unavailable
