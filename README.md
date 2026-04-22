# HyperBlue HVAC Multi-Agent BMS (LangGraph)

Semi-production-grade multi-agent HVAC control simulation using **LangGraph** with explicit agent boundaries, structured schemas, and deterministic oversight/safety layers.

## Highlights

- Stateful LangGraph workflow (not basic chain-style agents)
- Distinct nodes for planning, context/state, control decisioning, diagnostics, MPC-like oversight, safety/policy, and execution
- Diagnostics-aware routing: blocking failures halt execution before control application
- Tool layer with LangChain-style tools
- Mock building simulation with 3 rooms (campus scenario)
- Detailed logging for debugging and traceability
- Failure scenario coverage:
  - Missing data
  - Tool offline
  - Invalid ranges
  - Goal conflicts
  - Role-based access denial

## Project Structure

```text
.
├── agents/
│   ├── context_state.py
│   ├── diagnostics.py
│   ├── hvac_control.py
│   ├── mpc_oversight.py
│   ├── planning.py
│   └── safety_policy.py
├── environment/
│   └── simulator.py
├── graph/
│   └── bms_graph.py
├── tools/
│   └── bms_tools.py
├── examples/
│   └── run_demo.py
└── schemas.py
```

## Quick Start

1. Install dependencies:

```bash
pip install -U -r requirements.txt
```

2. Run demo:

```bash
python examples/run_demo.py
```

## Scenario Coverage in Demo

- **Normal operation** (staff role, valid targets)
- **Constraint violation stress** (high heat/CO2, policy+oversight moderation)
- **Role-based restriction** (student role denied control)
- **Tool offline diagnostics** (pre-execution blocking)
- **Missing telemetry** (`DATA_MISSING` blocks execution)

## Notes for Real BMS / EnergyPlus Extension

- Replace `environment/simulator.py` with live telemetry adapters.
- Keep tool signatures stable in `tools/bms_tools.py`.
- Replace simplified MPC (`agents/mpc_oversight.py`) with predictive controller while keeping same input/output model.
- Add richer comfort model (PMV/PPD), thermal dynamics, and forecast integration.
