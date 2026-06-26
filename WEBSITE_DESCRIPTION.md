---
title: "RoleForge - Production-Grade Agent Roles for AI Teams"
description: "31 validated agent roles for CrewAI, LangChain, and LangGraph. Free starter pack. Professional bundles from $49. Enterprise licenses available."
---

# RoleForge

## Stop Writing Prompts. Start Deploying Experts.

**RoleForge** is a framework-agnostic YAML library of **31 production-grade agent roles** across 7 domains, with ready-made adapters for CrewAI, LangChain, and LangGraph.

Most agent teams collapse because the system prompts are thin. "You are a helpful assistant" doesn't produce a Credit Risk Analyst. RoleForge gives you **deep, validated personas** that turn any framework into an expert team.

---

## What You Get

### The Roles (31, across 7 domains)

| Domain | Roles | Price |
|---|---|---|
| **Audit** | Lead Internal Auditor, IT Auditor, Compliance Auditor, Forensic Auditor, Audit Report Writer, BI Analyst | Part of bundles |
| **Risk** | Credit Risk Analyst, Operational Risk Manager, Enterprise Risk Strategist, Market Risk Quant, Scenario Modeler | Part of bundles |
| **Governance** | Board Liaison, Governance Analyst, Ethics Advisor | Part of bundles |
| **Philosophy** | Epistemology Reviewer, Ethics Culture Advisor, History of Philosophy Scholar, Logic & Argumentation Analyst | Part of bundles |
| **Creative Writing** | Narrative Architect, Character Developer, World Builder, Dialogue Specialist | Part of bundles |
| **Book Writing** | Developmental Editor, Copy Editor & Proofreader, Book Project Manager | Part of bundles |
| **Data Analysis** | Data Scientist, Data Storyteller, Data Governance Specialist, ML Engineer, Visualization Expert | Part of bundles |

### The Engine (Free Forever)

- **Framework adapters** — turn any role into a CrewAI Agent, LangChain Chain, or LangGraph Node
- **Role registry** — search, filter, and discover roles by domain or task
- **LLM-powered recommender** — describe your task in plain English, get the right agent
- **9 LangGraph templates** — supervisor-worker, debate, reflection loop, human-in-the-loop, map-reduce, and more
- **Full validation** — JSON Schema + Pydantic + 43 unit tests

---

## Pricing

### Free Tier
✅ **Starter Pack** — 3 high-quality roles + overlays. Build something real before paying.

Personal projects, education, research, internal business, and startups under $1M ARR are all free.

### Professional Bundles (One-Time Purchase)

| Tier | Price | What's Included |
|---|---|---|
| **Domain Pack** | **$49** | All roles in ONE domain + overlays + examples |
| **Professional Pack** | **$99** | 3 domains + graph templates + priority support |
| **Complete Bundle** ⭐ | **$199** | All 31 roles + 12mo updates + Discord community |
| **Enterprise License** | **$499** | Everything + commercial rights + 5 custom roles + dedicated support |

**Why this pricing?** Market research shows prompt marketplaces price at $3-$15 (hobbyist territory). RoleForge is a professional tool, positioned between commodity prompts and enterprise frameworks. See our [market research analysis](https://github.com/majidrajpar/roleforge/blob/main/research_output/market_research_report.md) for the full data.

**The rule:** Build with it for free. Extract commercial value from it? License it.

See [COMMERCIAL_LICENSE.md](https://github.com/majidrajpar/roleforge/blob/main/COMMERCIAL_LICENSE.md) for full terms.

---

## Quick Start

```bash
# Clone the repository
git clone https://github.com/majidrajpar/roleforge.git
cd roleforge

# Install dependencies
uv sync

# Validate all 31 roles
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

# Turn it into a CrewAI Agent
adapter = CrewAIAdapter(context)
agent = adapter.adapt(role)
```

---

## Built By

RoleForge is maintained by [Your Name / Company](https://majidrajpar.github.io/portfolio_my/roleforge/).

- [GitHub Repository](https://github.com/majidrajpar/roleforge)
- [Contributing Guide](https://github.com/majidrajpar/roleforge/blob/main/CONTRIBUTING.md)
- [Changelog](https://github.com/majidrajpar/roleforge/blob/main/CHANGELOG.md)
- [Market Research Report](https://github.com/majidrajpar/roleforge/blob/main/research_output/market_research_report.md)
- [Contact for Licensing](mailto:majidrajpar@gmail.com)

---

*Commercialization is a virtue. Open source is a strategy. This is both.*
