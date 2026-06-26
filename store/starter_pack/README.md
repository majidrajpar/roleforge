# RoleForge Starter Pack

**FREE FOREVER** — No license required.

## What's Included

3 production-grade agent roles with framework overlays:

1. **Data Scientist** (`data_scientist`) — Data analysis, ML, statistics
2. **Narrative Architect** (`narrative_architect`) — Story structure, plot design
3. **Ethics Advisor** (`ethics_advisor`) — AI ethics, governance, compliance

Each role includes:
- Framework-agnostic YAML definition
- CrewAI overlay (goal, backstory)
- LangGraph overlay (node type)

## Quick Start

```python
from loader import RoleRegistry
from adapters.crewai_adapter import CrewAIAdapter

registry = RoleRegistry()
registry.index()
role = registry.get("data_scientist")
```

## License

These 3 roles are released under the **MIT License**.

The RoleForge engine (adapters, registry, validators) is also free under MIT.

---

**Want more?** Upgrade to the [Complete Bundle](https://gumroad.com/your-store) for all 31 roles across 7 domains.

**Building commercially?** See [COMMERCIAL_LICENSE.md](../COMMERCIAL_LICENSE.md) for redistribution rights.
