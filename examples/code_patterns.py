"""
Code Inclusion Patterns for the Agent Roles Library.

This module shows the canonical ways to include and use the library in your projects.
"""
from __future__ import annotations

# =============================================================================
# PATTERN 1: Direct Import (When src/ is in PYTHONPATH)
# =============================================================================

# If pyproject.toml pythonpath includes "src", or you've added it:
from loader import RoleRegistry
from models import RuntimeContext
from adapters.crewai_adapter import CrewAIAdapter
from adapters.langchain_adapter import LangChainAdapter
from adapters.langgraph_adapter import LangGraphAdapter
from role_selector import RoleSelector, LLMRoleRecommender
from graphs.templates import (
    create_sequential_pipeline_graph,
    create_fan_out_graph,
    create_debate_graph,
)


# =============================================================================
# PATTERN 2: Runtime Path Insertion (Scripts, Notebooks)
# =============================================================================

def setup_imports():
    """Add src/ to sys.path for runtime imports."""
    import sys
    from pathlib import Path
    
    # For scripts in examples/ or project root
    src_path = str(Path(__file__).parent / "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    # For graphs/ (if not in src/)
    root_path = str(Path(__file__).parent)
    if root_path not in sys.path:
        sys.path.insert(0, root_path)


# =============================================================================
# PATTERN 3: Notebook Import
# =============================================================================

# In Jupyter notebooks (cells):
"""
import sys
from pathlib import Path

# If notebook is in examples/
sys.path.insert(0, str(Path.cwd().parent / "src"))
sys.path.insert(0, str(Path.cwd().parent))

# If notebook is in project root
# sys.path.insert(0, str(Path.cwd() / "src"))
"""


# =============================================================================
# PATTERN 4: Using the Role Selector (Query → Agent)
# =============================================================================

def example_role_selector():
    """Find the best agents for a task."""
    from role_selector import RoleSelector
    
    selector = RoleSelector()
    
    # Single agent recommendation
    results = selector.recommend(
        "I need to audit cloud infrastructure",
        top_k=3
    )
    # Returns: [{id, name, category, description, score, expertise, responsibilities}]
    
    # Multi-agent team composition
    team = selector.recommend_team(
        "Write a governance policy for AI usage",
        team_size=4
    )
    # Returns diverse team across categories
    
    # Browse by category
    categories = selector.list_categories()
    # ['audit', 'book_writing', 'creative_writing', 'data_analysis', 'governance', 'philosophy', 'risk']
    
    # Get specific role details
    role = selector.get_role_by_id("operational_risk_manager")
    # Returns: {id, name, category, description, responsibilities, expertise, tools, tags}


# =============================================================================
# PATTERN 5: Creating Framework-Specific Agents
# =============================================================================

def example_crewai_agent():
    """Create a CrewAI agent from a role definition."""
    from crewai import LLM
    from loader import RoleRegistry
    from models import RuntimeContext
    from adapters.crewai_adapter import CrewAIAdapter
    
    # 1. Load role with overlay
    registry = RoleRegistry()
    registry.index()
    role, overlay = registry.get_role_with_overlay("lead_internal_auditor", "crewai")
    
    # 2. Create runtime context
    llm = LLM(model="kimi-k2.7-code:cloud", base_url="...", api_key="...")
    context = RuntimeContext(llm=llm, tools=[], allow_delegation=True)
    
    # 3. Adapt to CrewAI Agent
    adapter = CrewAIAdapter(context)
    agent = adapter.adapt(role, overlay.data if overlay else None)
    
    # agent is now a crewai.Agent instance
    return agent


def example_langchain_chain():
    """Create a LangChain chain from a role definition."""
    from langchain_core.language_models.fake import FakeListLLM
    from loader import RoleRegistry
    from models import RuntimeContext
    from adapters.langchain_adapter import LangChainAdapter
    
    # 1. Load role
    registry = RoleRegistry()
    registry.index()
    role = registry.get("data_scientist")
    
    # 2. Create runtime context with tools
    llm = FakeListLLM(responses=["Analysis complete"])
    context = RuntimeContext(llm=llm, tools=[])
    
    # 3. Adapt to LangChain chain
    adapter = LangChainAdapter(context)
    chain = adapter.adapt(role)
    
    # chain is now an LCEL runnable
    return chain


def example_langgraph_node():
    """Create a LangGraph node from a role definition."""
    from loader import RoleRegistry
    from models import RuntimeContext
    from adapters.langgraph_adapter import LangGraphAdapter
    
    # 1. Load role
    registry = RoleRegistry()
    registry.index()
    role = registry.get("narrative_architect")
    
    # 2. Create runtime context (state_schema required for LangGraph)
    context = RuntimeContext(llm=llm, tools=[], state_schema=dict)
    
    # 3. Adapt to LangGraph node function
    adapter = LangGraphAdapter(context)
    node = adapter.adapt(role)
    
    # node is now a callable (state, config) -> state
    return node


# =============================================================================
# PATTERN 6: Building Graph Workflows
# =============================================================================

def example_sequential_pipeline():
    """Build a sequential pipeline of agents."""
    from loader import RoleRegistry
    from models import RuntimeContext
    from graphs.templates import create_sequential_pipeline_graph
    
    registry = RoleRegistry()
    registry.index()
    
    # Load roles for pipeline
    roles = [
        registry.get("narrative_architect"),
        registry.get("character_developer"),
        registry.get("developmental_editor"),
    ]
    
    # Create graph
    context = RuntimeContext(llm=llm, tools=[])
    graph = create_sequential_pipeline_graph(roles=roles, runtime_context=context)
    
    return graph


def example_fan_out():
    """Build a fan-out graph with parallel workers."""
    from loader import RoleRegistry
    from models import RuntimeContext
    from graphs.templates import create_fan_out_graph
    
    registry = RoleRegistry()
    registry.index()
    
    aggregator = registry.get("lead_internal_auditor")
    workers = [
        registry.get("operational_risk_manager"),
        registry.get("compliance_auditor"),
        registry.get("it_auditor"),
    ]
    
    context = RuntimeContext(llm=llm, tools=[])
    graph = create_fan_out_graph(
        aggregator_role=aggregator,
        worker_roles=workers,
        runtime_context=context,
    )
    
    return graph


# =============================================================================
# PATTERN 7: Working with Overlays
# =============================================================================

def example_overlay_usage():
    """Understand overlay precedence and loading."""
    from loader import RoleRegistry
    
    registry = RoleRegistry()
    registry.index()
    
    # Core role (framework-agnostic)
    role = registry.get("lead_internal_auditor")
    # Contains: id, name, category, description, responsibilities, expertise, tools
    
    # CrewAI overlay (optional framework hints)
    crewai_overlay = registry.get_overlay("crewai", "lead_internal_auditor")
    # Contains: goal, backstory, allow_delegation
    
    # LangGraph overlay (optional framework hints)
    langgraph_overlay = registry.get_overlay("langgraph", "lead_internal_auditor")
    # Contains: node_type (agent_node, supervisor, worker)
    
    # Precedence: Core fields are canonical. Overlays are adapter-specific overrides.
    
    # Get both at once
    role, overlay = registry.get_role_with_overlay("lead_internal_auditor", "crewai")


# =============================================================================
# PATTERN 8: Complete End-to-End Example
# =============================================================================

def complete_example():
    """Full workflow: Query -> Recommend -> Adapt -> Execute."""
    import sys
    from pathlib import Path
    
    # Setup
    sys.path.insert(0, str(Path(__file__).parent / "src"))
    
    from crewai import LLM, Task, Crew
    from loader import RoleRegistry
    from role_selector import RoleSelector
    from models import RuntimeContext
    from adapters.crewai_adapter import CrewAIAdapter
    
    # Step 1: Get recommendations for a task
    selector = RoleSelector()
    recommendations = selector.recommend(
        "Assess credit risk and market risk in our trading portfolio",
        top_k=2
    )
    
    # Step 2: Load recommended roles with overlays
    registry = RoleRegistry()
    registry.index()
    
    # Step 3: Create agents
    llm = LLM(model="kimi-k2.7-code:cloud", base_url="...", api_key="...")
    context = RuntimeContext(llm=llm, tools=[])
    adapter = CrewAIAdapter(context)
    
    agents = []
    for rec in recommendations:
        role, overlay = registry.get_role_with_overlay(rec["id"], "crewai")
        agent = adapter.adapt(role, overlay.data if overlay else None)
        agents.append(agent)
    
    # Step 4: Create tasks
    tasks = [
        Task(description="Analyze credit risk exposure", expected_output="Risk report", agent=agents[0]),
        Task(description="Analyze market risk exposure", expected_output="Risk report", agent=agents[1]),
    ]
    
    # Step 5: Execute
    crew = Crew(agents=agents, tasks=tasks)
    result = crew.kickoff()
    
    return result


if __name__ == "__main__":
    print("This module contains code inclusion patterns for the Agent Roles Library.")
    print("Import the patterns you need into your own scripts.")
    print("\nAvailable patterns:")
    print("  1. Direct Import (when src/ is in PYTHONPATH)")
    print("  2. Runtime Path Insertion (scripts, notebooks)")
    print("  3. Role Selector (query -> agent matching)")
    print("  4. CrewAI Agent Creation")
    print("  5. LangChain Chain Creation")
    print("  6. LangGraph Node Creation")
    print("  7. Graph Workflow Building")
    print("  8. Overlay Usage")
    print("  9. Complete End-to-End Example")
