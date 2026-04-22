# HyperBlue HVAC Multi-Agent BMS (LangGraph)

Semi-production-grade multi-agent HVAC control simulation using **LangGraph** with explicit agent boundaries, structured schemas, and deterministic oversight/safety layers.

## Highlights

- Stateful LangGraph workflow (not basic chain-style agents)
- Distinct nodes for planning, context/state, control decisioning, diagnostics, MPC-like oversight, safety/policy, and execution
- **Gemini 2.5 Flash support** for Planning Agent (`gemini-2.5-flash`) with deterministic fallback when API/deps are unavailable
- Diagnostics-aware routing: blocking failures halt execution before control application
- Tool layer with LangChain-style tools
- Mock building simulation with 3 rooms (campus scenario)

## Project Structure

```text
.
├── agents/
├── config/
│   └── settings.py
├── environment/
├── examples/
├── graph/
├── llm/
│   └── gemini_client.py
├── tools/
├── .env
├── .env.example
├── requirements.txt
└── schemas.py
```

## Quick Start

1. Install dependencies:

```bash
pip install -U -r requirements.txt
```

2. Configure environment variables in `.env`:

```bash
GOOGLE_API_KEY=your_google_api_key_here
PLANNER_MODEL=gemini-2.5-flash
HVAC_MODEL=gemini-2.5-flash
```

3. Run demo:

```bash
python examples/run_demo.py
```

## Behavior with/without Gemini

- If `GOOGLE_API_KEY` + `langchain-google-genai` are available, Planning Agent uses Gemini 2.5 Flash to generate structured orchestration tasks.
- If not available, system automatically falls back to deterministic planning logic (no crash).

## Scenario Coverage in Demo

- Normal operation
- Constraint violation stress
- Role-based restriction
- Tool offline diagnostics
- Missing telemetry

## Notes for Real BMS / EnergyPlus Extension

- Replace `environment/simulator.py` with live telemetry adapters.
- Keep tool signatures stable in `tools/bms_tools.py`.
- Replace simplified MPC (`agents/mpc_oversight.py`) with predictive controller while keeping same input/output model.
