"""
CrewAI adapter for the Agent Roles Library.
"""
from __future__ import annotations

from typing import Any

from crewai import Agent

from models import RoleDefinition, RuntimeContext
from adapters.base import BaseAdapter


class CrewAIAdapter(BaseAdapter):
    """
    Adapts RoleDefinition instances into CrewAI Agent objects.
    """
    framework = "crewai"

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
            prompt += "\nRecommended tools:\n"
            for tool in role.recommended_tools:
                prompt += f"- {tool}\n"
        return prompt

    def _synthesize_goal(self, role: RoleDefinition, overlay: dict[str, Any] | None) -> str:
        """Synthesize goal from overlay or role description + responsibilities."""
        if overlay and "goal" in overlay:
            return overlay["goal"]
        # Synthesize from first responsibility + description
        goal = role.responsibilities[0] if role.responsibilities else role.description[:100]
        return goal

    def _synthesize_backstory(self, role: RoleDefinition, overlay: dict[str, Any] | None) -> str:
        """Synthesize backstory from overlay or role expertise + description."""
        if overlay and "backstory" in overlay:
            return overlay["backstory"]
        # Synthesize from expertise
        backstory = f"You are an experienced {role.name.lower()} with deep knowledge in: "
        backstory += ", ".join(role.expertise) + "."
        return backstory

    def adapt(self, role: RoleDefinition, overlay: dict[str, Any] | None = None) -> Agent:
        """
        Adapt a RoleDefinition into a CrewAI Agent.
        """
        goal = self._synthesize_goal(role, overlay)
        backstory = self._synthesize_backstory(role, overlay)
        allow_delegation = overlay.get("allow_delegation", self.runtime_context.allow_delegation) if overlay else self.runtime_context.allow_delegation

        agent = Agent(
            role=role.name,
            goal=goal,
            backstory=backstory,
            llm=self.runtime_context.llm,
            tools=self.runtime_context.tools,
            memory=self.runtime_context.memory,
            allow_delegation=allow_delegation,
            verbose=True,
        )
        return agent
