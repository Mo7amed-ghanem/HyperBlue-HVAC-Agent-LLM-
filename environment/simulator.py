from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Optional

from schemas import EnvironmentState, RoomState


@dataclass
class MockBmsEnvironment:
    """Mock campus HVAC environment.

    Deterministic and easily replaceable by EnergyPlus/IoT adapters.
    """

    tool_health: Dict[str, bool] = field(
        default_factory=lambda: {
            "get_room_state": True,
            "get_outdoor_weather": True,
            "get_occupancy": True,
            "get_co2_level": True,
            "apply_mpc_targets": True,
            "check_tool_status": True,
            "get_user_role": True,
        }
    )
    outdoor_temp_c: float = 33.0
    rooms: Dict[str, Dict] = field(
        default_factory=lambda: {
            "ENGR-101": {"temp": 27.5, "co2": 1100, "occupancy": 35, "mode": "cooling"},
            "LIB-204": {"temp": 24.2, "co2": 820, "occupancy": 12, "mode": "ventilation"},
            "CHEM-110": {"temp": 29.0, "co2": 1350, "occupancy": 40, "mode": "cooling"},
        }
    )

    def get_full_state(self) -> EnvironmentState:
        return EnvironmentState(
            timestamp=datetime.now(tz=timezone.utc).isoformat(),
            outdoor_temp_c=self.outdoor_temp_c,
            rooms=[
                RoomState(
                    room_id=room,
                    indoor_temp_c=data.get("temp"),
                    co2_ppm=data.get("co2"),
                    occupancy=data.get("occupancy"),
                    hvac_mode=data.get("mode", "off"),
                )
                for room, data in self.rooms.items()
            ],
            hvac_online=self.tool_health["apply_mpc_targets"],
        )

    def get_room_state(self, room_id: str) -> Dict:
        return self.rooms.get(room_id, {})

    def get_occupancy(self, room_id: str) -> Optional[int]:
        room = self.rooms.get(room_id)
        return room.get("occupancy") if room else None

    def get_co2_level(self, room_id: str) -> Optional[int]:
        room = self.rooms.get(room_id)
        return room.get("co2") if room else None

    def get_outdoor_weather(self) -> Dict:
        return {"outdoor_temp_c": self.outdoor_temp_c}

    def apply_targets(self, zone_targets: Dict[str, float], fan_speed_pct: int, fresh_air_pct: int) -> str:
        for zone, target in zone_targets.items():
            if zone in self.rooms and self.rooms[zone].get("temp") is not None:
                current = self.rooms[zone]["temp"]
                self.rooms[zone]["temp"] = round(current + (target - current) * 0.4, 2)
                self.rooms[zone]["mode"] = "cooling" if target < current else "heating"
                current_co2 = self.rooms[zone].get("co2")
                if current_co2 is not None:
                    self.rooms[zone]["co2"] = max(450, int(current_co2 - fresh_air_pct * 1.2))
        return f"Applied {len(zone_targets)} zones @ fan={fan_speed_pct}% fresh_air={fresh_air_pct}%"

    def set_tool_health(self, tool_name: str, is_online: bool) -> None:
        self.tool_health[tool_name] = is_online

    def check_tool_status(self, tool_name: str) -> bool:
        return self.tool_health.get(tool_name, False)

    def inject_missing_data(self, room_id: str, field_name: str) -> None:
        if room_id in self.rooms:
            self.rooms[room_id][field_name] = None
