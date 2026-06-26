# AGENTS.md — Agent Roles Library

## Quick Commands

| Task | Command |
|---|---|
| Run all tests | `uv run pytest tests/` |
| Validate roles library | `uv run python validate_roles.py` |
| Run usage demo | `uv run python examples/usage.py` |
| Run role selection demo | `uv run python examples/role_selection_demo.py` |
| Start Jupyter | `uv run jupyter notebook examples/` |

## Import Path Quirk

All `src/` modules are imported **without** the `src.` prefix in both library code and tests. `pyproject.toml` sets `pythonpath = ["src"]`, and scripts add `sys.path.insert(0, str(Path(...) / "src"))`. If you see `ModuleNotFoundError: No module named 'src'`, check that `sys.path` includes the project root or `src/` directory.

## Architecture

This is a **framework-agnostic YAML core** with tailored Python adapters:

- **Core:** YAML role definitions in `roles/{category}/` — validated by JSON Schema + Pydantic.
- **Overlays:** Framework-specific hints in `overlays/{framework}/` (e.g., `crewai/`, `langgraph/`).
- **Adapters:** Consume `RoleDefinition` **+** `RuntimeContext` (model, tools, memory). Do not assume YAML is fully portable.
- **Templates:** Pre-built LangGraph patterns in `graphs/templates.py`.
- **Selection:** `src/role_selector.py` provides `RoleSelector` (keyword) and `LLMRoleRecommender` (semantic) to match queries to agents.

### Key Models

- `RoleDefinition` — framework-agnostic role schema (`id`, `name`, `category`, `description`, `responsibilities`, `expertise`, `recommended_tools`).
- `RuntimeContext` — supplied at adapter runtime (`llm`, `tools`, `memory`, `state_schema`, `allow_delegation`).
- `Overlay` — optional framework-specific override map.

## Adding a New Role

1. Create YAML in `roles/{category}/{role_id}.yaml` following `schemas/role.schema.json`.
2. Optionally create overlays in `overlays/crewai/{role_id}.yaml` and/or `overlays/langgraph/{role_id}.yaml`.
3. Run `uv run python validate_roles.py` to verify.
4. Add unit tests if needed (see `tests/test_core.py` for patterns).

## Adapter Contract

Adapters implement `BaseAdapter` (`src/adapters/base.py`):
- `build_system_prompt(role)` — portable persona string.
- `adapt(role, overlay)` — returns framework-native object (`crewai.Agent`, LCEL chain, LangGraph node function).

**CrewAI:** Maps `name` → `role`, synthesizes `goal`/`backstory` from overlay or `description` + top 2 responsibilities.
**LangChain:** Builds system prompt, returns `prompt | llm` chain with tools bound.
**LangGraph:** Returns node builder function injecting system prompt; requires `state_schema` in `RuntimeContext`.

## LangGraph Templates

Located in `graphs/templates.py`:
- **Sequential Pipeline** — linear chain.
- **Fan-Out** — parallel workers → aggregator.
- **Supervisor-Worker** — supervisor delegates to workers.
- **Reflection Loop** — producer ↔ reviewer iteration.
- **Hierarchical Teams** — orchestrator → team leads → workers.
- **Human-in-the-Loop** — breakpoint for human approval.
- **Conditional Routing** — router → specialists by keyword.
- **Map-Reduce** — parallel mappers → reducer.
- **Debate** — proposition vs opposition → judge verdict.

## Examples

- `examples/usage.py` — basic CrewAI/LangChain/LangGraph usage.
- `examples/role_selection_demo.py` — query → agent matching demos.
- `examples/01_crewai_integration.ipynb` — CrewAI notebook.
- `examples/02_langchain_integration.ipynb` — LangChain notebook.
- `examples/03_langgraph_integration.ipynb` — LangGraph notebook.

All examples add `src/` to `sys.path` at runtime. Notebooks require `sys.path.insert(0, str(Path.cwd().parent / "src"))`.

## Validation

- **Deterministic:** JSON Schema (`schemas/role.schema.json`) + Pydantic validators (`src/validators.py`) check description length, duplicate responsibilities, cross-role overlap.
- **Manual:** `validate_roles.py` reports role counts, category breakdown, and overlay coverage.
- **Tests:** `tests/test_core.py` (32 tests) covers models, loaders, registry, adapters, graph templates. `tests/test_role_selector.py` (11 tests) covers selection logic.

## API Key

Examples use LLM APIs. Set your key via environment variable:
```bash
export OLLAMA_API_KEY="your-api-key-here"
```

## Dependencies

Managed by `uv`. Key packages: `crewai`, `langchain`, `langgraph`, `pydantic`, `pyyaml`, `pytest`, `jupyter`. See `pyproject.toml` for full list.

## License

Elastic License 2.0. Free for community use, education, and embedding in products.
Commercial SaaS/managed service use requires a license.
See LICENSE file for details.
