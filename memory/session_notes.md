# RoleForge — Session Notes & Project History

**Repo:** https://github.com/majidrajpar/roleforge  
**Website:** https://majidrajpar.github.io/portfolio_my/roleforge/  
**Last Updated:** 2026-06-26

---

## What This Project Is

RoleForge is a framework-agnostic YAML library of **31 production-grade AI agent roles** with ready-made adapters for CrewAI, LangChain, and LangGraph. It replaces fragile ad-hoc system prompts with deep, validated personas.

- **Free tier:** 3 roles + full engine (Data Scientist, Narrative Architect, Ethics Advisor)
- **Paid tiers:** 28 premium roles in bundles ($49–$499)
- **License:** Elastic License 2.0 (free for personal/internal; commercial redistribution requires Enterprise License)

---

## Full Session History

### Phase 1: Core Development

**What we built:**

- YAML role definitions for 31 agents across 7 domains
- Framework adapters: CrewAI, LangChain, LangGraph
- 9 pre-built LangGraph graph templates (supervisor-worker, debate, map-reduce, etc.)
- Role registry with keyword + LLM-powered search
- 43 tests with JSON Schema validation
- Pydantic models for `RoleDefinition`, `RuntimeContext`, `Overlay`
- Example scripts and Jupyter notebooks

**Key files created:**

- `src/models.py` — Pydantic schemas
- `src/loader.py` — YAML loading + registry
- `src/validators.py` — Deterministic validation
- `src/role_selector.py` — Keyword + semantic role matching
- `src/adapters/` — CrewAI, LangChain, LangGraph adapters
- `graphs/templates.py` — LangGraph patterns
- `schemas/role.schema.json` — JSON Schema validation
- `roles/{category}/` — 31 YAML role definitions
- `overlays/{framework}/` — Framework-specific hints
- `examples/` — Usage demos and notebooks

### Phase 2: Premium Removal & Git History Erasure

**Why:** Prevent premium role piracy via Git history.

**What we did:**

1. Deleted 28 premium roles from `roles/` and `overlays/`
2. Kept only 3 free roles: `data_scientist.yaml`, `narrative_architect.yaml`, `ethics_advisor.yaml`
3. Erased Git history entirely:
   - Created orphan branch: `git checkout --orphan main`
   - Committed reduced repo
   - Force-pushed to GitHub
4. Result: Public repo has **exactly 1 commit** with only free roles

**Remaining premium roles exist ONLY on local machine** at:

```
C:\Users\sorat\Desktop\Coding\portfolio_my\roleforge\store\starter_pack\
```

And in the original backup directories (not in Git).

### Phase 3: Commercialization Setup

**Store directory (`store/`):**

Created product READMEs for 5 pricing tiers:

| Tier | Price | What You Get |
|---|---|---|
| Starter Pack | $49 | 10 roles (most popular domains) |
| Professional | $149 | 20 roles |
| Enterprise | $499 | All 31 roles + custom overlays |
| Audit Bundle | $99 | 6 audit-specific roles |
| Data Science Bundle | $99 | 5 data science roles |

**License file (`COMMERCIAL_LICENSE.md`):**

- Elastic License 2.0 terms
- Tier descriptions and pricing
- Redistribution rules

**Bundle packaging script (`tools/package_bundles.py`):**

- Reads premium roles from local `store/starter_pack/`
- Generates ZIP files for each Gumroad tier
- Includes README + roles + overlays + license

### Phase 4: Website Integration

**Website URL:** https://majidrajpar.github.io/portfolio_my/roleforge/

**What we updated:**

- Replaced all `your-website.com/roleforge` placeholders across the repo
- Updated: `launch_kit/*.md`, `README.md`, `WEBSITE_DESCRIPTION.md`, `LAUNCH_CHECKLIST.md`, `AGENTS.md`
- Committed and pushed: `cb8a62a`

### Phase 5: Formatting Fix

**Issue:** A PowerShell `-replace` command accidentally flattened all `.md` files to single lines.

**Fix:**

- Rewrote all 4 launch kit files with proper line breaks
- Committed: `789ee28`
- Files restored: `HACKER_NEWS.md`, `REDDIT.md`, `LINKEDIN.md`, `TWITTER.md`

### Phase 6: Folder Organization

**What we did:**

- Created `memory/` — this file and future session notes
- Created `tools/` — dev scripts: `validate_roles.py`, `package_bundles.py`, `market_research_agent.py`, `market_research_agent_v2.py`, `langgraph_pricing_advisor.py`
- Created `archive/research/` — old market research outputs
- Moved files accordingly
- Updated references in docs

**Commit:** (to be made)

---

## Key Decisions Made

| Decision | Rationale |
|---|---|
| **3 free roles** | Proven enough to evaluate, not enough to replace paid bundles |
| **History erasure** | Elastic License 2.0 allows redistribution; Git history = free piracy |
| **One-time pricing** | User preference: "no subscriptions" |
| **Product-first marketing** | No prices in social posts; single link to website |
| **Gumroad for distribution** | Simple, supports one-time pricing, ZIP downloads |
| **Store directory in repo** | Product pages live in repo; actual role files sold via Gumroad |
| **Local-only premium roles** | ZIP generation requires local files; GitHub only has free tier |

---

## File Organization

```
roleforge/
├── .github/workflows/     # CI/CD (pytest, validate)
├── archive/
│   └── research/            # Old market research outputs
├── examples/                # Usage demos, notebooks, quick_demo.py
├── graphs/
│   └── templates.py         # 9 LangGraph patterns
├── launch_kit/              # Social media posts (HN, Reddit, LinkedIn, Twitter)
├── memory/
│   └── session_notes.md     # This file
├── overlays/                # Framework-specific hints (3 crewai + 3 langgraph)
├── roles/                   # YAML role definitions (3 free roles only)
├── schemas/
│   └── role.schema.json     # JSON Schema for validation
├── src/                     # Core library code
│   ├── adapters/            # CrewAI, LangChain, LangGraph adapters
│   ├── loader.py            # Registry + YAML loading
│   ├── models.py            # Pydantic schemas
│   ├── role_selector.py     # Keyword + LLM matching
│   └── validators.py        # Deterministic validation
├── store/                   # Product pages, pricing tiers
├── tests/                   # 43 pytest tests
├── tools/                   # Dev scripts (validate, package, research)
├── AGENTS.md                # Developer quick-reference
├── CHANGELOG.md             # Version history
├── COMMERCIAL_LICENSE.md    # License + pricing tiers
├── CONTRIBUTING.md          # Contribution guidelines
├── LAUNCH_CHECKLIST.md      # Step-by-step launch guide
├── LICENSE                  # Elastic License 2.0
├── README.md                # Main project README
├── WEBSITE_DESCRIPTION.md   # Website copy
└── pyproject.toml           # Dependencies + tool config
```

---

## Launch Kit Contents

All posts link to the GitHub repo and the portfolio website.

| Platform | File | Tone |
|---|---|---|
| Hacker News | `launch_kit/HACKER_NEWS.md` | Technical, problem/solution |
| Reddit | `launch_kit/REDDIT.md` | Detailed, TL;DR, questions |
| LinkedIn | `launch_kit/LINKEDIN.md` | C-suite, authority positioning |
| Twitter/X | `launch_kit/TWITTER.md` | Thread format, 8 tweets |

---

## Next Steps (Outstanding)

1. **Gumroad setup** — Create products, upload ZIP bundles from `tools/package_bundles.py`
2. **Launch posts** — Publish from `launch_kit/` on HN, Reddit, LinkedIn, Twitter
3. **Monitor feedback** — GitHub issues, stars, community requests
4. **New domains** — Healthcare, Legal, Security based on demand
5. **Framework integrations** — AutoGen, LlamaIndex if requested

---

## Critical Reminders

- **Repo is public** with only 3 free roles. Premium roles are **local-only**.
- **Git history is clean** — 1 commit, no trace of premium roles.
- **Website URL** is `https://majidrajpar.github.io/portfolio_my/roleforge/`
- **Bundle generation** requires premium roles to exist in `store/starter_pack/` (local only).
- **Tests pass** with the reduced 3-role catalog (43 tests).

---

*Built with Python, Pydantic, YAML, and a lot of prompt engineering discipline.*
