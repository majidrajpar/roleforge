# RoleForge

**31 production-grade agent roles. One YAML library. Three framework adapters. Zero prompt engineering.**

RoleForge is the fastest way to build coherent AI agent teams. Stop writing ad-hoc system prompts. Start deploying expert personas that work across CrewAI, LangChain, and LangGraph.

---

## Why RoleForge?

Most agent teams fail because the prompts are fragile. "You are a helpful assistant" doesn't cut it when you need a Credit Risk Analyst or a Forensic Auditor.

RoleForge gives you:

- **31 validated roles** across Audit, Risk, Governance, Philosophy, Creative Writing, Book Writing, and Data Analysis
- **Framework adapters** that turn YAML into CrewAI Agents, LangChain Chains, or LangGraph Nodes
- **Smart matching** — point a query at the library and get the right agent, automatically
- **Graph templates** — 9 pre-built LangGraph patterns (supervisor-worker, debate, map-reduce, human-in-the-loop, and more)
- **Full test coverage** — 43 tests, JSON Schema validation, Pydantic models

---

## Quick Start

```bash
# Clone the repository
git clone https://github.com/majidrajpar/roleforge.git
cd roleforge

# Install dependencies with uv
uv sync

# Validate all roles
uv run python validate_roles.py

# Run tests
uv run pytest tests/
```

```python
from loader import RoleRegistry
from adapters.crewai_adapter import CrewAIAdapter

# Load a role
registry = RoleRegistry()
registry.index()
role = registry.get("lead_internal_auditor")

# Adapt to CrewAI Agent
adapter = CrewAIAdapter(context)
agent = adapter.adapt(role)
```

See [examples/](examples/) for CrewAI, LangChain, and LangGraph integrations.

---

## What's Included

| Domain | Roles | Use Case |
|---|---|---|
| **Audit** | 6 | Internal audit, IT audit, compliance, forensic investigation |
| **Risk** | 5 | Credit, operational, enterprise, scenario modeling |
| **Governance** | 3 | Board liaison, governance analysis, ethics |
| **Philosophy** | 4 | Epistemology, ethics, metaphysics, logic |
| **Creative Writing** | 4 | Narrative architect, character developer, world builder, dialogue |
| **Book Writing** | 3 | Developmental editor, copy editor, project manager |
| **Data Analysis** | 5 | Data scientist, storyteller, governance, ML engineer, visualization |

---

## Project Structure

```
roleforge/
├── roles/              # 31 framework-agnostic role YAMLs
├── overlays/           # Framework-specific overlays (CrewAI, LangGraph)
├── src/
│   ├── models.py      # RoleDefinition, RuntimeContext
│   ├── loader.py      # YAML loading & registry
│   ├── validators.py  # Deterministic validation
│   ├── role_selector.py # Query-to-agent matching
│   └── adapters/      # CrewAI, LangChain, LangGraph
├── graphs/            # 9 pre-built LangGraph patterns
├── schemas/           # JSON Schema for role validation
├── tests/             # 43 unit tests
└── examples/          # Jupyter notebooks & usage demos
```

---

## Pricing: Free to Build, Pay for Convenience

The **core engine is free** under the Elastic License 2.0. Use it for personal projects, education, research, internal business, and even startups under $1M ARR.

Want to save time? Buy validated role packs (one-time purchase, lifetime access):

| Tier | Price | What You Get |
|---|---|---|
| **Starter Pack** | **Free** | 3 roles + overlays. Build something real before paying. |
| **Domain Pack** | **$49** | All roles in one domain (e.g., Audit: 6 roles) + overlays |
| **Professional Pack** | **$99** | 3 domains + graph templates + priority support |
| **Complete Bundle** ⭐ | **$199** | All 31 roles + 12mo updates + Discord |
| **Enterprise License** | **$499** | Everything + commercial rights + 5 custom roles + dedicated support |

**Why this pricing?** Market research shows prompt marketplaces sell at $3-$15 (hobbyist territory). RoleForge is a professional tool, priced between commodity prompts and enterprise frameworks. See [research_output/market_research_report.md](research_output/market_research_report.md) for the full analysis.

**The rule:** Build with it for free. Extract commercial value from it? License it.

See [COMMERCIAL_LICENSE.md](COMMERCIAL_LICENSE.md) for full details and [LICENSE](LICENSE) for the legal text.

---

## Contributing

We welcome contributions. See [CONTRIBUTING.md](CONTRIBUTING.md) for how to add roles, submit PRs, and run tests.

---

## Questions?

- **Docs:** See [AGENTS.md](AGENTS.md) for detailed architecture and conventions
- **Issues:** [GitHub Issues](https://github.com/majidrajpar/roleforge/issues)
- **Commercial:** [majidrajpar@gmail.com](mailto:majidrajpar@gmail.com)

---

<sub>Built by [Your Name](https://your-website.com). Commercialization is a virtue.</sub>
