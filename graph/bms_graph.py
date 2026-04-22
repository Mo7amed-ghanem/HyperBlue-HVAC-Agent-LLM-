from __future__ import annotations

import logging
from typing import Any, Dict, List, TypedDict

from langgraph.graph import END, START, StateGraph

from agents.diagnostics import feasibility_diagnostics_agent
from agents.hvac_control import hvac_control_agent
from agents.mpc_oversight import mpc_oversight_agent
from agents.planning import planning_agent
from agents.safety_policy import safety_policy_agent
from environment.simulator import MockBmsEnvironment
from schemas import (
    EnvironmentState,
    ExecutionResult,
    GoalRequest,
    HvacTargets,
    OversightResult,
    SafetyDecision,
    UserRole,
)
from tools.bms_tools import BmsToolbox

logger = logging.getLogger(__name__)


class BmsGraphState(TypedDict, total=False):
    goal: GoalRequest
    user_role: UserRole
    planner_task: Dict[str, Any]
    env_state: Dict[str, Any]
    tool_failures: List[str]
    hvac_proposal: Dict[str, Any]
    diagnostics: Dict[str, Any]
    oversight: Dict[str, Any]
    safety: Dict[str, Any]
    execution: Dict[str, Any]


def build_bms_graph(env: MockBmsEnvironment):
    def planning_node(state: BmsGraphState):
        task = planning_agent(state["goal"])
        return {"planner_task": task.model_dump()}

    def context_node(state: BmsGraphState):
        logger.info("Context/state agent: collecting structured telemetry")
        tools = BmsToolbox(env, state["user_role"].value)
        tool_failures = []
        for tool_name in ["get_room_state", "get_outdoor_weather", "get_occupancy", "get_co2_level"]:
            if not tools.check_tool_status.invoke({"tool_name": tool_name}):
                tool_failures.append(tool_name)

        env_state = env.get_full_state()
        return {"env_state": env_state.model_dump(), "tool_failures": tool_failures}

    def hvac_control_node(state: BmsGraphState):
        env_state = EnvironmentState.model_validate(state["env_state"])
        proposal = hvac_control_agent(state["goal"], env_state)
        return {"hvac_proposal": proposal.model_dump()}

    def diagnostics_node(state: BmsGraphState):
        report = feasibility_diagnostics_agent(
            goal=state["goal"],
            env_state=EnvironmentState.model_validate(state["env_state"]),
            proposal=HvacTargets.model_validate(state["hvac_proposal"]),
            unavailable_tools=state.get("tool_failures", []),
        )
        return {"diagnostics": report.model_dump()}

    def mpc_node(state: BmsGraphState):
        result = mpc_oversight_agent(
            EnvironmentState.model_validate(state["env_state"]),
            HvacTargets.model_validate(state["hvac_proposal"]),
        )
        return {"oversight": result.model_dump()}

    def safety_node(state: BmsGraphState):
        adjusted = OversightResult.model_validate(state["oversight"]).adjusted_targets
        decision = safety_policy_agent(state["user_role"], adjusted)
        return {"safety": decision.model_dump()}

    def execution_node(state: BmsGraphState):
        logger.info("Execution layer: applying approved targets")
        tools = BmsToolbox(env, state["user_role"].value)
        safety = SafetyDecision.model_validate(state["safety"])

        if not safety.approved:
            result = ExecutionResult(success=False, message=safety.reason)
            return {"execution": result.model_dump()}

        approved = safety.sanitized_targets
        if approved is None:
            result = ExecutionResult(success=False, message="No approved targets available")
            return {"execution": result.model_dump()}

        if not tools.check_tool_status.invoke({"tool_name": "apply_mpc_targets"}):
            result = ExecutionResult(success=False, message="Execution tool unavailable")
            return {"execution": result.model_dump()}

        msg = tools.apply_mpc_targets.invoke(
            {
                "zone_targets": approved.zone_targets_c,
                "fan_speed_pct": approved.fan_speed_pct,
                "fresh_air_pct": approved.fresh_air_pct,
            }
        )
        result = ExecutionResult(success=True, message=msg, applied_targets=approved)
        return {"execution": result.model_dump()}

    graph = StateGraph(BmsGraphState)
    graph.add_node("planning", planning_node)
    graph.add_node("context_state", context_node)
    graph.add_node("hvac_control", hvac_control_node)
    graph.add_node("diagnostics", diagnostics_node)
    graph.add_node("mpc_oversight", mpc_node)
    graph.add_node("safety_policy", safety_node)
    graph.add_node("execution", execution_node)

    graph.add_edge(START, "planning")
    graph.add_edge("planning", "context_state")
    graph.add_edge("context_state", "hvac_control")
    graph.add_edge("hvac_control", "diagnostics")
    graph.add_edge("diagnostics", "mpc_oversight")
    graph.add_edge("mpc_oversight", "safety_policy")
    graph.add_edge("safety_policy", "execution")
    graph.add_edge("execution", END)

    return graph.compile()
