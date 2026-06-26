# Show HN: RoleForge — 31 production-grade agent roles for AI teams

**Problem:** Building agent teams with CrewAI/LangGraph means writing ad-hoc system prompts. "You are a helpful assistant" doesn't produce a Credit Risk Analyst.

**Solution:** A framework-agnostic YAML library of 31 validated agent personas with ready-made adapters for CrewAI, LangChain, and LangGraph.

**What it does:**

- Gives you deep, validated personas instead of fragile prompt engineering
- 31 roles across 7 domains: Audit, Risk, Governance, Philosophy, Creative Writing, Book Writing, Data Analysis
- Each role includes framework-specific overlays (CrewAI goals/backstories, LangGraph node types)
- Full engine: adapters, registry, validators, 9 pre-built graph templates
- 43 tests, JSON Schema validation, clean architecture

**Free starter pack:**

- 3 roles: Data Scientist, Narrative Architect, Ethics Advisor
- Full engine included
- One `pip install` away

**Why this matters:** We validated the market — no curated agent role library exists. Closest thing is prompt marketplaces selling $3 snippets with no validation, no framework integration, and no test coverage.

**Repo:** https://github.com/majidrajpar/roleforge

**Pricing and bundles:** https://majidrajpar.github.io/portfolio_my/roleforge/

**Built with:** Python, Pydantic, YAML, and a lot of prompt engineering discipline.

Feedback welcome. Especially interested in:

- Which domains need more roles?
- Framework integrations we should prioritize?
- What would make you actually use this in production?
