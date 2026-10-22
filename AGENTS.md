# AGENTS.md — RoleForge Agent Roles Library

## Quick Commands

| Task | Command |
|---|---|
| Run all tests | `uv run pytest tests/` |
| Validate roles library | `uv run python tools/validate_roles.py` |
| Run usage demo | `uv run python examples/usage.py` |
| Run role selection demo | `uv run python examples/role_selection_demo.py` |
| Start Jupyter | `uv run jupyter notebook examples/` |

## Import Path Quirk

All `src/` modules are imported **without** the `src.` prefix in both library code and tests. `pyproject.toml` sets `pythonpath = ["src"]`, and scripts add `sys.path.insert(0, str(Path(...) / "src"))`. If you see `ModuleNotFoundError: No module named 'src'`, check that `sys.path` includes the project root or `src/` directory.

## Architecture

This is a **framework-agnostic YAML core** with tailored Python adapters, distributed as tiered packs via the `store/` directory.

- **Core library (`src/`):** `RoleDefinition`, `RoleLoader`, `RoleRegistry`, `RoleValidator`, adapters (CrewAI, LangChain, LangGraph), and `RoleSelector`/`LLMRoleRecommender` for semantic role matching. Framework-agnostic and stable.
- **Roles (`roles/{category}/`):** Three starter roles ship in the repo — `data_analysis/data_scientist`, `philosophy/ethics_advisor`, `creative_writing/narrative_architect`. Each is a YAML file validated against `schemas/role.schema.json` + Pydantic.
- **Overlays (`overlays/{framework}/`):** Framework-specific hints for each of the three starter roles, under `crewai/` and `langgraph/`.
- **Store (`store/`):** Tiered distribution packs — `starter_pack/` (3 roles, mirrors the in-repo roles+overlays), `professional_pack/`, `enterprise_bundle/`, `complete_bundle/`, `domain_packs/`. Each pack is self-contained with its own README. The store is the commercial/product surface; the `roles/`+`overlays/` directories are the open-core sample.
- **Templates (`graphs/templates.py`):** Pre-built LangGraph patterns (sequential, fan-out, supervisor-worker, reflection, hierarchical, HITL, conditional routing, map-reduce, debate).
- **Tools (`tools/`):** `validate_roles.py` (library validator), `market_research_agent.py` / `market_research_agent_v2.py` (research agents used during product validation), `package_bundles.py` (store packager), `langgraph_pricing_advisor.py` (pricing tool).
- **Launch kit (`launch_kit/`):** Draft posts for Hacker News, LinkedIn, Reddit, Twitter — used for the public launch, kept for reference.

### Key Models

- `RoleDefinition` — framework-agnostic role schema (`id`, `name`, `category`, `description`, `responsibilities`, `expertise`, `recommended_tools`, `domain_tags`).
- `RuntimeContext` — supplied at adapter runtime (`llm`, `tools`, `memory`, `state_schema`, `allow_delegation`).
- `Overlay` — optional `dict[str, Any]` loaded from `overlays/{framework}/{role_id}.yaml` that overrides or extends role fields at adapter runtime.

## Adding a New Role

1. Create YAML in `roles/{category}/{role_id}.yaml` following `schemas/role.schema.json`.
2. Optionally create overlays in `overlays/crewai/{role_id}.yaml` and/or `overlays/langgraph/{role_id}.yaml`.
3. Run `uv run python tools/validate_roles.py` to verify.
4. If the role belongs in a commercial pack, also add it to the relevant `store/{pack}/` directory and regenerate via `tools/package_bundles.py`.
5. Add unit tests if needed (see `tests/test_core.py` for patterns).

## opencode Integration

RoleForge roles can be exported as opencode subagents. The repo ships the 3 free
starter roles in `roles/`; the 28 paid roles are stored locally outside the repo at
`~/.config/opencode/roleforge/roles/` to keep the public repo an open-core sample.

- `uv run python tools/restore_paid_roles.py` — re-extract the 28 paid roles + 56
  overlays from the repo's git history (`70fb922^`) into the local catalog dir.
  Idempotent; re-run to recover or refresh the catalog.
- `uv run python tools/export_opencode_agents.py` — validate the combined 31-role
  catalog and write one opencode subagent to `~/.config/opencode/agent/<role_id>.md`.
  Run with `--dry-run` to preview, `--role <id>` to export a subset, `--free-only`
  for just the starter roles.

After adding or editing a role, re-run the export script, then restart opencode to
pick up the regenerated agents.

## Adapter Contract

Adapters implement `BaseAdapter` (`src/adapters/base.py`):
- `__init__(runtime_context)` — store the `RuntimeContext` (model, tools, memory, etc.).
- `build_system_prompt(role)` — portable persona string.
- `adapt(role, overlay=None)` — returns framework-native object (`crewai.Agent`, LCEL chain, LangGraph node function).

**CrewAI:** Maps `name` → `role`, synthesizes `goal`/`backstory` from overlay or `responsibilities[0]` / role expertise.
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
- `examples/quick_demo.py` — minimal smoke test.
- `examples/01_crewai_integration.ipynb` — CrewAI notebook.
- `examples/02_langchain_integration.ipynb` — LangChain notebook.
- `examples/03_langgraph_integration.ipynb` — LangGraph notebook.

All examples add `src/` to `sys.path` at runtime. Notebooks require `sys.path.insert(0, str(Path.cwd().parent / "src"))`.

## Validation

- **Deterministic:** JSON Schema (`schemas/role.schema.json`) + Pydantic validators (`src/validators.py`) check description length, duplicate responsibilities, cross-role overlap.
- **Manual:** `tools/validate_roles.py` reports role counts, category breakdown, and overlay coverage.
- **Tests:** `tests/test_core.py` (32 tests) covers models, loaders, registry, adapters, graph templates. `tests/test_role_selector.py` (11 tests) covers selection logic. Total: 43 tests, all passing.

## API Key

Examples use LLM APIs. Set the appropriate key for your provider via environment variable:
```bash
export OPENAI_API_KEY="your-api-key-here"
# or ANTHROPIC_API_KEY, etc.
```

## Dependencies

Managed by `uv`. Key packages: `crewai`, `langchain`, `langgraph`, `pydantic`, `pyyaml`, `pytest`, `jupyter`. See `pyproject.toml` for full list.

## CI

GitHub Actions workflow at `.github/workflows/ci.yml` runs `uv sync` + `uv run pytest tests/` on push and PR.

## License

Elastic License 2.0. Free for community use, education, and embedding in products.
Commercial SaaS/managed service use requires a license.
See `COMMERCIAL_LICENSE.md` and `LICENSE` for details.

## Repository Notes

- The `archive/research/` directory contains market-research outputs used during product validation (raw LLM responses, recommendation JSONs, research reports). Kept for traceability, not part of the shipped library.
- The `memory/` directory holds session notes from the build process — not user-facing.
- The `response_to_jamie*.md` files are reviewer-feedback responses from the product-validation cycle.