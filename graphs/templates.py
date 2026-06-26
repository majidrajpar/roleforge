"""
Pre-built LangGraph templates for common multi-agent patterns.
"""
from __future__ import annotations

from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

from src.models import RoleDefinition, RuntimeContext
from src.adapters.langgraph_adapter import LangGraphAdapter


class AgentState(TypedDict):
    """Base state schema for LangGraph templates."""
    messages: Annotated[list[BaseMessage], add_messages]
    next: str  # Routing key


def create_supervisor_worker_graph(
    supervisor_role: RoleDefinition,
    worker_roles: list[RoleDefinition],
    runtime_context: RuntimeContext,
    supervisor_overlay: dict | None = None,
    worker_overlays: list[dict] | None = None,
) -> StateGraph:
    """
    Create a Supervisor-Worker LangGraph.

    The supervisor delegates tasks to workers and synthesizes their outputs.
    """
    if runtime_context.state_schema is None:
        runtime_context.state_schema = AgentState

    adapter = LangGraphAdapter(runtime_context)
    builder = StateGraph(runtime_context.state_schema)

    # Add supervisor node
    supervisor_node = adapter.adapt(supervisor_role, supervisor_overlay)
    builder.add_node("supervisor", supervisor_node)

    # Add worker nodes
    worker_overlays = worker_overlays or [{} for _ in worker_roles]
    for i, (role, overlay) in enumerate(zip(worker_roles, worker_overlays)):
        node_name = f"worker_{i}"
        worker_node = adapter.adapt(role, overlay)
        builder.add_node(node_name, worker_node)

    # Define edges: supervisor -> workers -> supervisor -> END
    def route_from_supervisor(state: AgentState) -> str:
        # Simple routing: if supervisor says "done", end; else delegate to next worker
        last_message = state["messages"][-1].content if state["messages"] else ""
        if "done" in last_message.lower():
            return END
        # Round-robin or based on state["next"]
        return state.get("next", "worker_0")

    builder.set_entry_point("supervisor")
    for i in range(len(worker_roles)):
        builder.add_edge(f"worker_{i}", "supervisor")
        builder.add_conditional_edges(
            "supervisor",
            route_from_supervisor,
            {f"worker_{i}": f"worker_{i}", END: END},
        )

    return builder.compile()


def create_fan_out_graph(
    aggregator_role: RoleDefinition,
    worker_roles: list[RoleDefinition],
    runtime_context: RuntimeContext,
    aggregator_overlay: dict | None = None,
    worker_overlays: list[dict] | None = None,
) -> StateGraph:
    """
    Create a Fan-Out LangGraph.

    All workers process in parallel, then an aggregator synthesizes results.
    """
    if runtime_context.state_schema is None:
        runtime_context.state_schema = AgentState

    adapter = LangGraphAdapter(runtime_context)
    builder = StateGraph(runtime_context.state_schema)

    # Add aggregator node
    aggregator_node = adapter.adapt(aggregator_role, aggregator_overlay)
    builder.add_node("aggregator", aggregator_node)

    # Add worker nodes
    worker_overlays = worker_overlays or [{} for _ in worker_roles]
    for i, (role, overlay) in enumerate(zip(worker_roles, worker_overlays)):
        node_name = f"worker_{i}"
        worker_node = adapter.adapt(role, overlay)
        builder.add_node(node_name, worker_node)

    # Entry -> all workers in parallel
    builder.set_entry_point("worker_0")
    for i in range(1, len(worker_roles)):
        builder.add_edge("__start__", f"worker_{i}")

    # All workers -> aggregator
    for i in range(len(worker_roles)):
        builder.add_edge(f"worker_{i}", "aggregator")

    # Aggregator -> END
    builder.add_edge("aggregator", END)

    return builder.compile()


def create_sequential_pipeline_graph(
    roles: list[RoleDefinition],
    runtime_context: RuntimeContext,
    overlays: list[dict] | None = None,
) -> StateGraph:
    """
    Create a Sequential Pipeline LangGraph.

    Roles pass output down a linear chain.
    """
    if runtime_context.state_schema is None:
        runtime_context.state_schema = AgentState

    adapter = LangGraphAdapter(runtime_context)
    builder = StateGraph(runtime_context.state_schema)

    # Add nodes
    overlays = overlays or [{} for _ in roles]
    node_names = []
    for i, (role, overlay) in enumerate(zip(roles, overlays)):
        node_name = f"step_{i}"
        node = adapter.adapt(role, overlay)
        builder.add_node(node_name, node)
        node_names.append(node_name)

    # Chain edges
    builder.set_entry_point(node_names[0])
    for i in range(len(node_names) - 1):
        builder.add_edge(node_names[i], node_names[i + 1])

    builder.add_edge(node_names[-1], END)

    return builder.compile()


def create_reflection_loop_graph(
    producer_role: RoleDefinition,
    reviewer_role: RoleDefinition,
    runtime_context: RuntimeContext,
    max_iterations: int = 3,
    producer_overlay: dict | None = None,
    reviewer_overlay: dict | None = None,
) -> StateGraph:
    """
    Create a Reflection Loop LangGraph.

    Producer generates output, reviewer critiques it, and the producer revises.
    Loops up to max_iterations or until reviewer approves.
    """
    if runtime_context.state_schema is None:
        runtime_context.state_schema = AgentState

    adapter = LangGraphAdapter(runtime_context)
    builder = StateGraph(runtime_context.state_schema)

    # Add nodes
    producer_node = adapter.adapt(producer_role, producer_overlay)
    reviewer_node = adapter.adapt(reviewer_role, reviewer_overlay)
    builder.add_node("producer", producer_node)
    builder.add_node("reviewer", reviewer_node)

    # Track iterations in state
    def route_from_reviewer(state: AgentState) -> str:
        last_message = state["messages"][-1].content if state["messages"] else ""
        iteration = state.get("iteration", 0)
        if "approve" in last_message.lower() or iteration >= max_iterations:
            return END
        return "producer"

    builder.set_entry_point("producer")
    builder.add_edge("producer", "reviewer")
    builder.add_conditional_edges(
        "reviewer",
        route_from_reviewer,
        {"producer": "producer", END: END},
    )

    return builder.compile()


# =============================================================================
# ADVANCED GRAPH TEMPLATES
# =============================================================================

class HierarchicalState(AgentState):
    """State schema for hierarchical team-of-teams pattern."""
    team_outputs: Annotated[list[dict], add_messages]
    final_synthesis: str


def create_hierarchical_teams_graph(
    team_leads: list[RoleDefinition],
    team_members_map: dict[str, list[RoleDefinition]],
    orchestrator_role: RoleDefinition,
    runtime_context: RuntimeContext,
    orchestrator_overlay: dict | None = None,
    team_lead_overlays: list[dict] | None = None,
    team_member_overlays_map: dict[str, list[dict]] | None = None,
) -> StateGraph:
    """
    Create a Hierarchical Team-of-Teams LangGraph.

    An orchestrator coordinates multiple team leads, each managing their own workers.
    Results bubble up: workers -> team leads -> orchestrator -> final synthesis.
    """
    if runtime_context.state_schema is None:
        runtime_context.state_schema = HierarchicalState

    adapter = LangGraphAdapter(runtime_context)
    builder = StateGraph(runtime_context.state_schema)

    # Add orchestrator node
    orchestrator_node = adapter.adapt(orchestrator_role, orchestrator_overlay)
    builder.add_node("orchestrator", orchestrator_node)

    # Add team lead nodes
    team_lead_overlays = team_lead_overlays or [{} for _ in team_leads]
    for i, (lead_role, overlay) in enumerate(zip(team_leads, team_lead_overlays)):
        lead_name = f"team_lead_{i}"
        lead_node = adapter.adapt(lead_role, overlay)
        builder.add_node(lead_name, lead_node)

        # Add workers for this team
        team_members = team_members_map.get(lead_role.id, [])
        member_overlays = (team_member_overlays_map or {}).get(lead_role.id, [{} for _ in team_members])
        for j, (member_role, member_overlay) in enumerate(zip(team_members, member_overlays)):
            member_name = f"team_{i}_member_{j}"
            member_node = adapter.adapt(member_role, member_overlay)
            builder.add_node(member_name, member_node)
            # Workers feed into team lead
            builder.add_edge(member_name, lead_name)

    # Team leads feed into orchestrator
    for i in range(len(team_leads)):
        builder.add_edge(f"team_lead_{i}", "orchestrator")

    # Orchestrator routes to teams or ends
    def route_orchestrator(state: HierarchicalState) -> str:
        last_message = state["messages"][-1].content if state["messages"] else ""
        if "synthesize" in last_message.lower() or "final" in last_message.lower():
            return END
        # Route to next team that hasn't processed
        return "team_lead_0"  # Simplified: could be dynamic

    builder.set_entry_point("orchestrator")
    builder.add_conditional_edges(
        "orchestrator",
        route_orchestrator,
        {f"team_lead_{i}": f"team_lead_{i}" for i in range(len(team_leads))} | {END: END},
    )

    return builder.compile()


class HumanLoopState(AgentState):
    """State schema for human-in-the-loop pattern."""
    human_feedback: str | None
    approved: bool
    iteration: int


def create_human_in_the_loop_graph(
    agent_role: RoleDefinition,
    reviewer_role: RoleDefinition,
    runtime_context: RuntimeContext,
    agent_overlay: dict | None = None,
    reviewer_overlay: dict | None = None,
    max_iterations: int = 5,
) -> StateGraph:
    """
    Create a Human-in-the-Loop LangGraph with breakpoints.

    Agent produces output -> Reviewer evaluates -> Human approves or provides feedback.
    If feedback provided, agent revises. Continues until approved or max iterations.
    """
    if runtime_context.state_schema is None:
        runtime_context.state_schema = HumanLoopState

    adapter = LangGraphAdapter(runtime_context)
    builder = StateGraph(runtime_context.state_schema)

    # Add agent node
    agent_node = adapter.adapt(agent_role, agent_overlay)
    builder.add_node("agent", agent_node)

    # Add reviewer node
    reviewer_node = adapter.adapt(reviewer_role, reviewer_overlay)
    builder.add_node("reviewer", reviewer_node)

    # Human feedback node (placeholder for actual human input)
    def human_feedback_node(state: HumanLoopState) -> HumanLoopState:
        """Breakpoint node that awaits human input."""
        # In production, this would pause and wait for external input
        # For now, simulate with state check
        return {
            "messages": state["messages"],
            "next": state.get("next", ""),
            "human_feedback": state.get("human_feedback", "Looks good"),
            "approved": "approve" in (state.get("human_feedback", "") or "").lower(),
            "iteration": state.get("iteration", 0) + 1,
        }

    builder.add_node("human_feedback", human_feedback_node)

    # Routing logic
    def route_after_human(state: HumanLoopState) -> str:
        if state.get("approved", False) or state.get("iteration", 0) >= max_iterations:
            return END
        return "agent"  # Revise based on feedback

    def route_after_reviewer(state: HumanLoopState) -> str:
        return "human_feedback"

    # Build graph
    builder.set_entry_point("agent")
    builder.add_edge("agent", "reviewer")
    builder.add_conditional_edges("reviewer", route_after_reviewer, {"human_feedback": "human_feedback"})
    builder.add_conditional_edges(
        "human_feedback",
        route_after_human,
        {"agent": "agent", END: END},
    )

    return builder.compile()


def create_conditional_routing_graph(
    roles: list[RoleDefinition],
    router_role: RoleDefinition,
    runtime_context: RuntimeContext,
    condition_map: dict[str, str],
    default_route: str = END,
    router_overlay: dict | None = None,
    role_overlays: list[dict] | None = None,
) -> StateGraph:
    """
    Create a Conditional Routing LangGraph.

    A router role analyzes input and dynamically routes to specialized roles
    based on content analysis. Uses a condition_map to map keywords to target nodes.
    """
    if runtime_context.state_schema is None:
        runtime_context.state_schema = AgentState

    adapter = LangGraphAdapter(runtime_context)
    builder = StateGraph(runtime_context.state_schema)

    # Add router node
    router_node = adapter.adapt(router_role, router_overlay)
    builder.add_node("router", router_node)

    # Add specialized role nodes
    role_overlays = role_overlays or [{} for _ in roles]
    node_names = []
    for i, (role, overlay) in enumerate(zip(roles, role_overlays)):
        node_name = f"specialist_{i}"
        node = adapter.adapt(role, overlay)
        builder.add_node(node_name, node)
        node_names.append(node_name)

    # Routing function
    def route_from_router(state: AgentState) -> str:
        last_message = state["messages"][-1].content if state["messages"] else ""
        content_lower = last_message.lower()

        # Check condition map
        for keyword, target in condition_map.items():
            if keyword.lower() in content_lower:
                return target

        return default_route

    # Build edges
    builder.set_entry_point("router")
    builder.add_conditional_edges(
        "router",
        route_from_router,
        {name: name for name in node_names} | {END: END},
    )

    # All specialists route back to router for potential re-routing
    for name in node_names:
        builder.add_edge(name, "router")

    return builder.compile()


class MapReduceState(AgentState):
    """State schema for map-reduce pattern."""
    chunks: list[str]
    processed_chunks: Annotated[list[str], add_messages]
    final_aggregation: str


def create_map_reduce_graph(
    mapper_roles: list[RoleDefinition],
    reducer_role: RoleDefinition,
    runtime_context: RuntimeContext,
    mapper_overlays: list[dict] | None = None,
    reducer_overlay: dict | None = None,
    aggregation_policy: str = "concatenate",
) -> StateGraph:
    """
    Create a Map-Reduce LangGraph.

    Input is split into chunks. Each mapper processes a chunk in parallel.
    Reducer aggregates all mapper outputs using the specified policy.
    """
    if runtime_context.state_schema is None:
        runtime_context.state_schema = MapReduceState

    adapter = LangGraphAdapter(runtime_context)
    builder = StateGraph(runtime_context.state_schema)

    # Add reducer node
    reducer_node = adapter.adapt(reducer_role, reducer_overlay)
    builder.add_node("reducer", reducer_node)

    # Add mapper nodes
    mapper_overlays = mapper_overlays or [{} for _ in mapper_roles]
    for i, (role, overlay) in enumerate(zip(mapper_roles, mapper_overlays)):
        mapper_name = f"mapper_{i}"
        mapper_node = adapter.adapt(role, overlay)
        builder.add_node(mapper_name, mapper_node)

    # Entry -> all mappers in parallel
    builder.set_entry_point("mapper_0")
    for i in range(1, len(mapper_roles)):
        builder.add_edge("__start__", f"mapper_{i}")

    # All mappers -> reducer
    for i in range(len(mapper_roles)):
        builder.add_edge(f"mapper_{i}", "reducer")

    # Reducer -> END (with aggregation logic in the reducer node itself)
    builder.add_edge("reducer", END)

    return builder.compile()


class DebateState(AgentState):
    """State schema for debate/adversarial pattern."""
    proposition: str
    arguments_for: Annotated[list[str], add_messages]
    arguments_against: Annotated[list[str], add_messages]
    rounds: int
    judge_verdict: str | None


def create_debate_graph(
    proposition_role: RoleDefinition,
    opposition_role: RoleDefinition,
    judge_role: RoleDefinition,
    runtime_context: RuntimeContext,
    num_rounds: int = 3,
    proposition_overlay: dict | None = None,
    opposition_overlay: dict | None = None,
    judge_overlay: dict | None = None,
) -> StateGraph:
    """
    Create a Debate / Adversarial LangGraph.

    Proposition and opposition roles alternate presenting arguments.
    A judge role evaluates after all rounds and delivers a verdict.
    Useful for adversarial validation, red-teaming, and critical analysis.
    """
    if runtime_context.state_schema is None:
        runtime_context.state_schema = DebateState

    adapter = LangGraphAdapter(runtime_context)
    builder = StateGraph(runtime_context.state_schema)

    # Add nodes
    prop_node = adapter.adapt(proposition_role, proposition_overlay)
    opp_node = adapter.adapt(opposition_role, opposition_overlay)
    judge_node = adapter.adapt(judge_role, judge_overlay)

    builder.add_node("proposition", prop_node)
    builder.add_node("opposition", opp_node)
    builder.add_node("judge", judge_node)

    # Round counter and routing
    def route_after_proposition(state: DebateState) -> str:
        current_round = state.get("rounds", 0)
        if current_round >= num_rounds:
            return "judge"
        return "opposition"

    def route_after_opposition(state: DebateState) -> str:
        current_round = state.get("rounds", 0)
        # Increment round after opposition speaks
        state["rounds"] = current_round + 1
        if state["rounds"] >= num_rounds:
            return "judge"
        return "proposition"

    def route_after_judge(state: DebateState) -> str:
        return END

    # Build graph
    builder.set_entry_point("proposition")
    builder.add_conditional_edges(
        "proposition",
        route_after_proposition,
        {"opposition": "opposition", "judge": "judge"},
    )
    builder.add_conditional_edges(
        "opposition",
        route_after_opposition,
        {"proposition": "proposition", "judge": "judge"},
    )
    builder.add_edge("judge", END)

    return builder.compile()
