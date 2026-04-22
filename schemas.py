from __future__ import annotations

from enum import Enum
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field, confloat


class UserRole(str, Enum):
    ADMIN = "Admin"
    STAFF = "Staff"
    STUDENT = "Student"


class ErrorType(str, Enum):
    DATA_MISSING = "DATA_MISSING"
    GOAL_CONFLICT = "GOAL_CONFLICT"
    TOOL_UNAVAILABLE = "TOOL_UNAVAILABLE"
    INVALID_RANGE = "INVALID_RANGE"


class RoomState(BaseModel):
    room_id: str
    indoor_temp_c: float
    co2_ppm: int
    occupancy: int
    hvac_mode: Literal["off", "cooling", "heating", "ventilation"]


class EnvironmentState(BaseModel):
    timestamp: str
    outdoor_temp_c: float
    rooms: List[RoomState]
    hvac_online: bool


class GoalRequest(BaseModel):
    improve_comfort: bool = True
    reduce_co2: bool = True
    optimize_energy: bool = True
    zone_scope: List[str] = Field(default_factory=list)
    weights: Dict[str, confloat(ge=0.0, le=1.0)] = Field(
        default_factory=lambda: {"comfort": 0.45, "energy": 0.3, "air_quality": 0.25}
    )


class PlannerTask(BaseModel):
    summary: str
    required_state_fields: List[str]
    objective_weights: Dict[str, float]


class HvacTargets(BaseModel):
    zone_targets_c: Dict[str, float]
    fan_speed_pct: int = Field(ge=0, le=100)
    fresh_air_pct: int = Field(ge=0, le=100)
    rationale: str


class DiagnosticIssue(BaseModel):
    error_type: ErrorType
    detail: str


class DiagnosticsReport(BaseModel):
    ok: bool
    issues: List[DiagnosticIssue] = Field(default_factory=list)


class OversightResult(BaseModel):
    adjusted_targets: HvacTargets
    overrides_applied: List[str] = Field(default_factory=list)


class SafetyDecision(BaseModel):
    approved: bool
    reason: str
    sanitized_targets: Optional[HvacTargets] = None


class ExecutionResult(BaseModel):
    success: bool
    message: str
    applied_targets: Optional[HvacTargets] = None
