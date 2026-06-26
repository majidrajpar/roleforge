"""
LangGraph adapter for the Agent Roles Library.
"""
from __future__ import annotations

from typing import Any, Callable

from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph

from models import RoleDefinition, RuntimeContext
from adapters.base import BaseAdapter


class LangGraphAdapter(BaseAdapter):
    """
    Adapts RoleDefinition instances into LangGraph node builder functions.
    """
    framework = "langgraph"

    def __init__(self, runtime_context: RuntimeContext):
        super().__init__(runtime_context)

    def build_system_prompt(self, role: RoleDefinition) -> str:
        """Build a system prompt from the role definition."""
        prompt = (
            f"You are a {role.name}.\n\n"
            f"{role.description}\n\n"
            f"Your responsibilities:\n"
        )
        for resp in role.responsibilities:
            prompt += f"- {resp}\n"
        prompt += "\nYour areas of expertise:\n"
        for exp in role.expertise:
            prompt += f"- {exp}\n"
        if role.recommended_tools:
            prompt += "\nAvailable capabilities:\n"
            for tool in role.recommended_tools:
                prompt += f"- {tool}\n"
        return prompt

    def adapt(self, role: RoleDefinition, overlay: dict[str, Any] | None = None) -> Callable:
        """
        Adapt a RoleDefinition into a LangGraph node builder function.
        Returns a callable that accepts (state, config) and returns updated state.
        """
        system_prompt = self.build_system_prompt(role)
        llm = self.runtime_context.llm
        tools = self.runtime_context.tools or []

        node_type = overlay.get("node_type", "agent_node") if overlay else "agent_node"

        def node_function(state: dict, config: RunnableConfig | None = None) -> dict:
            """
            LangGraph node function.
            Expects state to contain at least 'messages' key.
            """
            from langchain_core.messages import SystemMessage, HumanMessage

            messages = state.get("messages", [])

            # Inject system prompt at the beginning if not present
            if not messages or not isinstance(messages[0], SystemMessage):
                messages = [SystemMessage(content=system_prompt)] + messages

            # Prepare LLM with tools
            if tools:
                llm_with_tools = llm.bind_tools(tools)
            else:
                llm_with_tools = llm

            # Invoke LLM
            response = llm_with_tools.invoke(messages)

            # Return updated state
            return {"messages": messages + [response]}

        node_function.__name__ = f"{role.id}_node"
        node_function.__doc__ = f"LangGraph node for {role.name} ({node_type})"

        return node_function
