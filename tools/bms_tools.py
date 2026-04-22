from __future__ import annotations

import logging
from typing import Dict

from langchain_core.tools import tool

from environment.simulator import MockBmsEnvironment

logger = logging.getLogger(__name__)


class BmsToolbox:
    def __init__(self, env: MockBmsEnvironment, user_role: str):
        self.env = env
        self.user_role = user_role

    @tool
    def get_room_state(self, room_id: str) -> Dict:
        """Get room temperature, CO2, occupancy, and mode."""
        logger.debug("Tool get_room_state called for %s", room_id)
        return self.env.get_room_state(room_id)

    @tool
    def get_outdoor_weather(self) -> Dict:
        """Get outdoor weather state."""
        logger.debug("Tool get_outdoor_weather called")
        return self.env.get_outdoor_weather()

    @tool
    def get_occupancy(self, room_id: str) -> int | None:
        """Get occupancy for a room."""
        logger.debug("Tool get_occupancy called for %s", room_id)
        return self.env.get_occupancy(room_id)

    @tool
    def get_co2_level(self, room_id: str) -> int | None:
        """Get CO2 level for a room in ppm."""
        logger.debug("Tool get_co2_level called for %s", room_id)
        return self.env.get_co2_level(room_id)

    @tool
    def apply_mpc_targets(self, zone_targets: Dict[str, float], fan_speed_pct: int, fresh_air_pct: int) -> str:
        """Apply high-level approved HVAC targets (not actuator-level commands)."""
        logger.debug("Tool apply_mpc_targets called")
        return self.env.apply_targets(zone_targets, fan_speed_pct, fresh_air_pct)

    @tool
    def check_tool_status(self, tool_name: str) -> bool:
        """Check if a tool/system integration is available."""
        logger.debug("Tool check_tool_status called for %s", tool_name)
        return self.env.check_tool_status(tool_name)

    @tool
    def get_user_role(self) -> str:
        """Get caller role for RBAC policy."""
        logger.debug("Tool get_user_role called")
        return self.user_role
