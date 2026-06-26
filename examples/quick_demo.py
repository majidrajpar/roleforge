"""
RoleForge Quick Demo — 3 Free Starter Roles

Run this to see RoleForge in action with the free tier.
No API key required (uses mock LLMs).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from loader import RoleRegistry
from models import RuntimeContext
from adapters.crewai_adapter import CrewAIAdapter
from adapters.langchain_adapter import LangChainAdapter
from adapters.langgraph_adapter import LangGraphAdapter
from langchain_core.language_models.fake import FakeListLLM


def demo_registry():
    """Show role discovery with the free starter pack."""
    print("=" * 60)
    print("DEMO 1: Role Discovery")
    print("=" * 60)
    print()
    
    registry = RoleRegistry()
    registry.index()
    
    print(f"Total roles loaded: {len(registry.list_roles())}")
    print()
    
    print("Available roles:")
    for role in registry.list_roles():
        print(f"  - {role.name} ({role.category})")
    print()
    
    print("Search for 'data':")
    results = registry.search("data")
    for role in results:
        print(f"  → {role.name}: {role.description[:80]}...")
    print()


def demo_crewai():
    """Create a CrewAI agent from a free role."""
    print("=" * 60)
    print("DEMO 2: CrewAI Agent")
    print("=" * 60)
    print()
    
    registry = RoleRegistry()
    registry.index()
    
    role, overlay = registry.get_role_with_overlay("data_scientist", "crewai")
    
    # Use a mock LLM for demo purposes
    from crewai import LLM
    llm = LLM(
        model="kimi-k2.7-code:cloud",
        base_url="https://ollama.com/v1",
        api_key="demo-key",
    )
    
    context = RuntimeContext(llm=llm, tools=[], allow_delegation=False)
    adapter = CrewAIAdapter(context)
    agent = adapter.adapt(role, overlay.data if overlay else None)
    
    print(f"Created CrewAI Agent: {agent.role}")
    print(f"Goal: {agent.goal}")
    print(f"Backstory: {agent.backstory[:100]}...")
    print()


def demo_langchain():
    """Create a LangChain chain from a free role."""
    print("=" * 60)
    print("DEMO 3: LangChain Chain")
    print("=" * 60)
    print()
    
    registry = RoleRegistry()
    registry.index()
    role = registry.get("narrative_architect")
    
    mock_llm = FakeListLLM(responses=["A compelling story arc with three acts and a twist ending."])
    context = RuntimeContext(llm=mock_llm, tools=[])
    adapter = LangChainAdapter(context)
    chain = adapter.adapt(role)
    
    print(f"Created LangChain chain for: {role.name}")
    print(f"Invoke with: chain.invoke({{'input': 'Write a sci-fi story'}})")
    result = chain.invoke({"input": "Write a sci-fi story"})
    print(f"Result: {result}")
    print()


def demo_langgraph():
    """Create a LangGraph node from a free role."""
    print("=" * 60)
    print("DEMO 4: LangGraph Node")
    print("=" * 60)
    print()
    
    registry = RoleRegistry()
    registry.index()
    role = registry.get("ethics_advisor")
    
    mock_llm = FakeListLLM(responses=["This raises concerns about privacy and consent."])
    context = RuntimeContext(llm=mock_llm, tools=[], state_schema=dict)
    adapter = LangGraphAdapter(context)
    node = adapter.adapt(role)
    
    print(f"Created LangGraph node: {node.__name__}")
    print(f"Doc: {node.__doc__}")
    print(f"Callable: {callable(node)}")
    print()


def main():
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "ROLEFORGE QUICK DEMO" + " " * 27 + "║")
    print("║" + " " * 6 + "Free Starter Pack — 3 Roles" + " " * 23 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    demo_registry()
    demo_crewai()
    demo_langchain()
    demo_langgraph()
    
    print("=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  1. Clone the repo: git clone https://github.com/majidrajpar/roleforge")
    print("  2. Install: uv sync")
    print("  3. Build with the 3 free roles")
    print("  4. Upgrade for 28 more: https://gumroad.com (coming soon)")


if __name__ == "__main__":
    main()
