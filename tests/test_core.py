"""
Unit tests for the Agent Roles Library core infrastructure.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Add src to path for imports
src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Add project root to path for graphs
root_path = str(Path(__file__).parent.parent)
if root_path not in sys.path:
    sys.path.insert(0, root_path)

import pytest
from pathlib import Path

from models import RoleDefinition, RuntimeContext, Overlay
from loader import RoleLoader, RoleRegistry
from validators import RoleValidator, ValidationError
from adapters.crewai_adapter import CrewAIAdapter
from adapters.langchain_adapter import LangChainAdapter
from adapters.langgraph_adapter import LangGraphAdapter
from graphs.templates import (
    create_hierarchical_teams_graph,
    create_human_in_the_loop_graph,
    create_conditional_routing_graph,
    create_map_reduce_graph,
    create_debate_graph,
)


# === Fixtures ===

@pytest.fixture
def sample_role() -> RoleDefinition:
    return RoleDefinition(
        id="test_analyst",
        name="Test Analyst",
        category="test",
        domain_tags=["test", "analysis"],
        description="A test analyst role for unit testing purposes. This description must be at least fifty characters long.",
        responsibilities=["Analyze test data", "Generate test reports", "Validate test results"],
        expertise=["Test analysis", "Data validation"],
        recommended_tools=["test_tool"],
    )


@pytest.fixture
def runtime_context() -> RuntimeContext:
    # Mock LLM for testing
    class MockLLM:
        def invoke(self, messages):
            from langchain_core.messages import AIMessage
            return AIMessage(content="Mock response")
        def bind_tools(self, tools):
            return self
    
    return RuntimeContext(
        llm=MockLLM(),
        tools=[],
        memory=None,
        allow_delegation=False,
    )


# === Model Tests ===

class TestRoleDefinition:
    def test_valid_role(self, sample_role):
        assert sample_role.id == "test_analyst"
        assert sample_role.name == "Test Analyst"
        assert len(sample_role.responsibilities) == 3

    def test_invalid_id(self):
        with pytest.raises(ValueError):
            RoleDefinition(
                id="Invalid-ID-123",
                name="Invalid",
                category="test",
                description="This is a test description that is definitely more than fifty characters long.",
                responsibilities=["Test"],
                expertise=["Testing"],
            )

    def test_short_description(self):
        with pytest.raises(ValueError):
            RoleDefinition(
                id="short_desc",
                name="Short",
                category="test",
                description="Too short",
                responsibilities=["Test"],
                expertise=["Testing"],
            )

    def test_empty_responsibilities(self):
        with pytest.raises(ValueError):
            RoleDefinition(
                id="no_resp",
                name="No Resp",
                category="test",
                description="This is a test description that is definitely more than fifty characters long.",
                responsibilities=[],
                expertise=["Testing"],
            )


# === Loader Tests ===

class TestRoleLoader:
    def test_load_all_from_roles_dir(self):
        loader = RoleLoader()
        roles = loader.load_all()
        assert len(roles) == 3  # Starter pack: 3 free roles

    def test_load_specific_role(self):
        loader = RoleLoader()
        role = loader.load_role(Path("roles/data_analysis/data_scientist.yaml"))
        assert role.id == "data_scientist"
        assert role.category == "data_analysis"

    def test_load_all_categories(self):
        loader = RoleLoader()
        roles = loader.load_all()
        categories = set(r.category for r in roles)
        expected = {"philosophy", "creative_writing", "data_analysis"}  # Starter pack categories
        assert categories == expected


# === Registry Tests ===

class TestRoleRegistry:
    def test_index_and_get(self):
        registry = RoleRegistry()
        registry.index()
        role = registry.get("data_scientist")
        assert role is not None
        assert role.name == "Data Scientist"

    def test_search(self):
        registry = RoleRegistry()
        registry.index()
        results = registry.search("data")
        assert len(results) > 0

    def test_get_overlay(self):
        registry = RoleRegistry()
        registry.index()
        overlay = registry.get_overlay("crewai", "data_scientist")
        assert overlay is not None

    def test_all_roles_loaded(self):
        registry = RoleRegistry()
        registry.index()
        roles = registry.list_roles()
        assert len(roles) == 3  # Starter pack: 3 free roles

    def test_all_categories_present(self):
        registry = RoleRegistry()
        registry.index()
        roles = registry.list_roles()
        categories = set(r.category for r in roles)
        expected = {"philosophy", "creative_writing", "data_analysis"}
        assert categories == expected

    def test_crewai_overlay_count(self):
        registry = RoleRegistry()
        registry.index()
        crewai_overlays = [k for k in registry._overlays.keys() if k[0] == "crewai"]
        assert len(crewai_overlays) == 3  # Starter pack overlays

    def test_langgraph_overlay_count(self):
        registry = RoleRegistry()
        registry.index()
        langgraph_overlays = [k for k in registry._overlays.keys() if k[0] == "langgraph"]
        assert len(langgraph_overlays) == 3  # Starter pack overlays

    def test_supervisor_overlay(self):
        registry = RoleRegistry()
        registry.index()
        overlay = registry.get_overlay("langgraph", "data_scientist")
        assert overlay is not None


# === Validator Tests ===

class TestRoleValidator:
    def test_valid_role(self, sample_role):
        validator = RoleValidator([sample_role])
        errors = validator.validate(sample_role)
        assert len(errors) == 0

    def test_short_description_validation(self, sample_role):
        sample_role.description = "Short"
        validator = RoleValidator()
        errors = validator.validate(sample_role)
        assert any("description too short" in e for e in errors)

    def test_duplicate_responsibilities(self, sample_role):
        sample_role.responsibilities = ["Same task", "Same task", "Another task"]
        validator = RoleValidator()
        errors = validator.validate(sample_role)
        assert any("duplicate responsibility" in e for e in errors)

    def test_overlapping_across_roles(self, sample_role):
        role2 = RoleDefinition(
            id="test_analyst_2",
            name="Test Analyst 2",
            category="test",
            domain_tags=["test"],
            description="Another test analyst role with enough description length to pass validation.",
            responsibilities=["Analyze test data"],  # Overlaps with sample_role
            expertise=["Testing"],
        )
        validator = RoleValidator([sample_role, role2])
        errors = validator.validate_registry()
        assert any("Overlapping responsibility" in e for e in errors)

    def test_assert_valid_raises(self, sample_role):
        sample_role.description = "Short"
        validator = RoleValidator()
        with pytest.raises(ValidationError):
            validator.assert_valid(sample_role)


# === Adapter Tests ===

class TestCrewAIAdapter:
    def test_build_system_prompt(self, sample_role, runtime_context):
        adapter = CrewAIAdapter(runtime_context)
        prompt = adapter.build_system_prompt(sample_role)
        assert "Test Analyst" in prompt
        assert "Analyze test data" in prompt
        assert "Test analysis" in prompt

    def test_synthesize_goal(self, sample_role, runtime_context):
        adapter = CrewAIAdapter(runtime_context)
        goal = adapter._synthesize_goal(sample_role, None)
        assert "Analyze test data" in goal

    def test_synthesize_goal_with_overlay(self, sample_role, runtime_context):
        adapter = CrewAIAdapter(runtime_context)
        goal = adapter._synthesize_goal(sample_role, {"goal": "Custom goal"})
        assert goal == "Custom goal"


class TestLangChainAdapter:
    def test_build_system_prompt(self, sample_role, runtime_context):
        adapter = LangChainAdapter(runtime_context)
        prompt = adapter.build_system_prompt(sample_role)
        assert "Test Analyst" in prompt
        assert "Use the provided tools" in prompt


class TestLangGraphAdapter:
    def test_build_system_prompt(self, sample_role, runtime_context):
        adapter = LangGraphAdapter(runtime_context)
        prompt = adapter.build_system_prompt(sample_role)
        assert "Test Analyst" in prompt
        assert "Available capabilities" in prompt

    def test_adapt_returns_callable(self, sample_role, runtime_context):
        adapter = LangGraphAdapter(runtime_context)
        node = adapter.adapt(sample_role)
        assert callable(node)
        assert node.__name__ == "test_analyst_node"

    def test_node_execution(self, sample_role, runtime_context):
        adapter = LangGraphAdapter(runtime_context)
        node = adapter.adapt(sample_role)
        result = node({"messages": []})
        assert "messages" in result
        assert len(result["messages"]) > 0


# === Advanced Graph Template Tests ===

class TestHierarchicalTeamsGraph:
    def test_create_graph(self, sample_role, runtime_context):
        orchestrator = sample_role
        team_lead = RoleDefinition(
            id="team_lead", name="Team Lead", category="test",
            domain_tags=["test"],
            description="A test team lead role with enough description length to pass validation.",
            responsibilities=["Lead team"], expertise=["Leadership"],
        )
        member = RoleDefinition(
            id="team_member", name="Team Member", category="test",
            domain_tags=["test"],
            description="A test team member role with enough description length to pass validation.",
            responsibilities=["Execute tasks"], expertise=["Execution"],
        )
        graph = create_hierarchical_teams_graph(
            team_leads=[team_lead],
            team_members_map={"team_lead": [member]},
            orchestrator_role=orchestrator,
            runtime_context=runtime_context,
        )
        assert graph is not None


class TestHumanInTheLoopGraph:
    def test_create_graph(self, sample_role, runtime_context):
        reviewer = RoleDefinition(
            id="reviewer", name="Reviewer", category="test",
            domain_tags=["test"],
            description="A test reviewer role with enough description length to pass validation.",
            responsibilities=["Review work"], expertise=["Reviewing"],
        )
        graph = create_human_in_the_loop_graph(
            agent_role=sample_role,
            reviewer_role=reviewer,
            runtime_context=runtime_context,
            max_iterations=3,
        )
        assert graph is not None


class TestConditionalRoutingGraph:
    def test_create_graph(self, sample_role, runtime_context):
        router = RoleDefinition(
            id="router", name="Router", category="test",
            domain_tags=["test"],
            description="A test router role with enough description length to pass validation.",
            responsibilities=["Route tasks"], expertise=["Routing"],
        )
        specialist = RoleDefinition(
            id="specialist", name="Specialist", category="test",
            domain_tags=["test"],
            description="A test specialist role with enough description length to pass validation.",
            responsibilities=["Handle specialized tasks"], expertise=["Specialization"],
        )
        graph = create_conditional_routing_graph(
            roles=[sample_role, specialist],
            router_role=router,
            runtime_context=runtime_context,
            condition_map={"test": "specialist_0"},
        )
        assert graph is not None


class TestMapReduceGraph:
    def test_create_graph(self, sample_role, runtime_context):
        reducer = RoleDefinition(
            id="reducer", name="Reducer", category="test",
            domain_tags=["test"],
            description="A test reducer role with enough description length to pass validation.",
            responsibilities=["Aggregate results"], expertise=["Aggregation"],
        )
        graph = create_map_reduce_graph(
            mapper_roles=[sample_role, sample_role],
            reducer_role=reducer,
            runtime_context=runtime_context,
            aggregation_policy="concatenate",
        )
        assert graph is not None


class TestDebateGraph:
    def test_create_graph(self, sample_role, runtime_context):
        opposition = RoleDefinition(
            id="opposition", name="Opposition", category="test",
            domain_tags=["test"],
            description="A test opposition role with enough description length to pass validation.",
            responsibilities=["Argue against"], expertise=["Opposition"],
        )
        judge = RoleDefinition(
            id="judge", name="Judge", category="test",
            domain_tags=["test"],
            description="A test judge role with enough description length to pass validation.",
            responsibilities=["Evaluate arguments"], expertise=["Judging"],
        )
        graph = create_debate_graph(
            proposition_role=sample_role,
            opposition_role=opposition,
            judge_role=judge,
            runtime_context=runtime_context,
            num_rounds=2,
        )
        assert graph is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
