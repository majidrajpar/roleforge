"""
Usage example for the Agent Roles Library.
Demonstrates loading roles, applying adapters, and building LangGraphs.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from crewai import LLM as CrewAILLM
from langchain_core.language_models import BaseLanguageModel

from loader import RoleLoader, RoleRegistry
from models import RuntimeContext
from adapters.crewai_adapter import CrewAIAdapter
from adapters.langchain_adapter import LangChainAdapter
from adapters.langgraph_adapter import LangGraphAdapter
from graphs.templates import (
    create_supervisor_worker_graph,
    create_sequential_pipeline_graph,
)


def example_crewai():
    """Example: Create a CrewAI agent from a role definition."""
    print("=== CrewAI Example ===")
    
    # IMPORTANT: Set your API key via environment variable
    # export OLLAMA_API_KEY="your-api-key-here"
    api_key = os.getenv("OLLAMA_API_KEY", "your-api-key-here")

    # Load role
    registry = RoleRegistry()
    registry.index()
    role, overlay = registry.get_role_with_overlay("lead_internal_auditor", "crewai")

    # Create CrewAI LLM
    llm = CrewAILLM(
        model="kimi-k2.7-code:cloud",
        base_url="https://ollama.com/v1",
        api_key=api_key,
    )

    # Create runtime context
    context = RuntimeContext(llm=llm, tools=[], allow_delegation=True)

    # Adapt to CrewAI Agent
    adapter = CrewAIAdapter(context)
    agent = adapter.adapt(role, overlay.data if overlay else None)

    print(f"Created CrewAI Agent: {agent.role}")
    print(f"Goal: {agent.goal}")
    print(f"Backstory: {agent.backstory[:100]}...")
    print()


def example_langchain():
    """Example: Create a LangChain chain from a role definition."""
    print("=== LangChain Example ===")

    # Load role
    registry = RoleRegistry()
    registry.index()
    role = registry.get("data_scientist")

    # Create a simple mock LLM for demonstration
    from langchain_core.language_models.fake import FakeListLLM
    mock_llm = FakeListLLM(responses=["Mock analysis complete. The dataset shows interesting patterns."])

    # Create runtime context
    context = RuntimeContext(llm=mock_llm, tools=[])

    # Adapt to LangChain chain
    adapter = LangChainAdapter(context)
    chain = adapter.adapt(role)

    print(f"Created LangChain chain for: {role.name}")
    result = chain.invoke({"input": "Analyze this dataset"})
    print(f"Result: {result}")
    print()


def example_langgraph():
    """Example: Create a LangGraph with sequential pipeline."""
    print("=== LangGraph Example ===")

    # Load roles
    registry = RoleRegistry()
    registry.index()
    narrative_architect = registry.get("narrative_architect")
    developmental_editor = registry.get("developmental_editor")

    # Create a simple mock LLM for demonstration
    from langchain_core.language_models.fake import FakeListLLM
    mock_llm = FakeListLLM(responses=["Mock narrative arc designed.", "Mock editorial feedback provided."])

    # Create runtime context
    context = RuntimeContext(llm=mock_llm, tools=[])

    # Create sequential pipeline: Narrative Architect -> Developmental Editor
    graph = create_sequential_pipeline_graph(
        roles=[narrative_architect, developmental_editor],
        runtime_context=context,
    )

    print(f"Created LangGraph sequential pipeline:")
    print(f"  Step 1: {narrative_architect.name}")
    print(f"  Step 2: {developmental_editor.name}")
    print()


def example_registry_search():
    """Example: Search and discover roles."""
    print("=== Registry Search Example ===")
    registry = RoleRegistry()
    registry.index()

    # Search for risk-related roles
    results = registry.search("risk")
    print(f"Found {len(results)} roles matching 'risk':")
    for role in results:
        print(f"  - {role.name} ({role.category})")

    # Search for creative roles
    results = registry.search("creative")
    print(f"\nFound {len(results)} roles matching 'creative':")
    for role in results:
        print(f"  - {role.name} ({role.category})")
    print()


def main():
    print("Agent Roles Library - Usage Examples")
    print("=" * 60)
    print()

    example_registry_search()
    example_crewai()
    example_langchain()
    example_langgraph()

    print("=" * 60)
    print("All examples completed successfully!")


if __name__ == "__main__":
    main()
