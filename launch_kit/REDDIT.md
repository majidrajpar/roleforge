# Show HN: RoleForge — 31 production-grade agent roles for AI teams

**TL;DR:** Stop writing ad-hoc system prompts. Start deploying expert agents. Free starter pack included.

## The Problem

Most AI agent projects collapse because the prompts are thin. You can't build a reliable Credit Risk Analyst or Forensic Auditor with "You are a helpful assistant."

What you need are **deep, validated personas** — not fragile prompt engineering.

## What RoleForge Gives You

- **31 production-grade agent roles** across 7 domains: Audit, Risk, Governance, Philosophy, Creative Writing, Book Writing, Data Analysis
- **Framework adapters** for CrewAI, LangChain, and LangGraph — each role has specific overlays
- **Role registry** with keyword + LLM-powered search
- **9 pre-built LangGraph graph templates**: supervisor-worker, debate, map-reduce, human-in-the-loop, and more
- **43 tests + JSON Schema validation** — these aren't toy prompts, they're production-ready

## Free Starter Pack

- Data Scientist
- Narrative Architect
- Ethics Advisor

Plus the full engine. Build something real before deciding if you need more.

## The Tech

- YAML-based role definitions (framework-agnostic core)
- Pydantic validation + JSON Schema
- Python >= 3.11, uv for dependency management
- Clean architecture, no magic

## Market Validation

We built a LangGraph agent that searched the web for comparable products. Result: **no curated agent role library exists**. Closest analogues are prompt marketplaces selling $3 snippets that lack validation, framework integration, and test coverage.

First-mover advantage in a wide-open space.

## What's Next

We're building more domains (Healthcare? Legal? Security?) and adding framework integrations based on what the community actually needs.

**Repo:** https://github.com/majidrajpar/roleforge

**Pricing and bundles:** https://majidrajpar.github.io/portfolio_my/roleforge/

## Questions I'd Love Answered

1. What domains are missing?
2. Framework priority: CrewAI vs LangGraph vs AutoGen?
3. What's the biggest pain point in your current agent workflow?
4. Would you pay for validated roles if they saved you days of prompt engineering?
