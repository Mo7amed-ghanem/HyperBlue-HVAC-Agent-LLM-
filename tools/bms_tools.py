from __future__ import annotations

import logging
from typing import Any, Callable, Dict

from langchain_core.tools import StructuredTool

from environment.simulator import MockBmsEnvironment

logger = logging.getLogger(__name__)


class BmsToolbox:
    """LangChain tool wrapper over the mock environment.

    NOTE: Tools are created from bound callables in __init__ to avoid `self`
    leaking into the Pydantic input schema (common failure when decorating
    instance methods directly with @tool).
    """

    def __init__(self, env: MockBmsEnvironment, user_role: str):
        self.env = env
        self.user_role = user_role

        self.get_room_state = StructuredTool.from_function(
            func=self._get_room_state,
            name="get_room_state",
            description="Get room temperature, CO2, occupancy, and mode.",
        )
        self.get_outdoor_weather = StructuredTool.from_function(
            func=self._get_outdoor_weather,
            name="get_outdoor_weather",
            description="Get outdoor weather state.",
        )
        self.get_occupancy = StructuredTool.from_function(
            func=self._get_occupancy,
            name="get_occupancy",
            description="Get occupancy for a room.",
        )
        self.get_co2_level = StructuredTool.from_function(
            func=self._get_co2_level,
            name="get_co2_level",
            description="Get CO2 level for a room in ppm.",
        )
        self.apply_mpc_targets = StructuredTool.from_function(
            func=self._apply_mpc_targets,
            name="apply_mpc_targets",
            description="Apply approved high-level HVAC targets (not actuator commands).",
        )
        self.check_tool_status = StructuredTool.from_function(
            func=self._check_tool_status,
            name="check_tool_status",
            description="Check if a tool/system integration is available.",
        )
        self.get_user_role = StructuredTool.from_function(
            func=self._get_user_role,
            name="get_user_role",
            description="Get caller role for RBAC policy.",
        )

    def all_tools(self) -> Dict[str, StructuredTool]:
        return {
            "get_room_state": self.get_room_state,
            "get_outdoor_weather": self.get_outdoor_weather,
            "get_occupancy": self.get_occupancy,
            "get_co2_level": self.get_co2_level,
            "apply_mpc_targets": self.apply_mpc_targets,
            "check_tool_status": self.check_tool_status,
            "get_user_role": self.get_user_role,
        }

    def _get_room_state(self, room_id: str) -> Dict[str, Any]:
        logger.debug("Tool get_room_state called for %s", room_id)
        return self.env.get_room_state(room_id)

    def _get_outdoor_weather(self) -> Dict[str, Any]:
        logger.debug("Tool get_outdoor_weather called")
        return self.env.get_outdoor_weather()

    def _get_occupancy(self, room_id: str) -> int | None:
        logger.debug("Tool get_occupancy called for %s", room_id)
        return self.env.get_occupancy(room_id)

    def _get_co2_level(self, room_id: str) -> int | None:
        logger.debug("Tool get_co2_level called for %s", room_id)
        return self.env.get_co2_level(room_id)

    def _apply_mpc_targets(self, zone_targets: Dict[str, float], fan_speed_pct: int, fresh_air_pct: int) -> str:
        logger.debug("Tool apply_mpc_targets called")
        return self.env.apply_targets(zone_targets, fan_speed_pct, fresh_air_pct)

    def _check_tool_status(self, tool_name: str) -> bool:
        logger.debug("Tool check_tool_status called for %s", tool_name)
        return self.env.check_tool_status(tool_name)

    def _get_user_role(self) -> str:
        logger.debug("Tool get_user_role called")
        return self.user_role
