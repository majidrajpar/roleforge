"""
LangChain adapter for the Agent Roles Library.
"""
from __future__ import annotations

from typing import Any

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableSequence

from models import RoleDefinition, RuntimeContext
from adapters.base import BaseAdapter


class LangChainAdapter(BaseAdapter):
    """
    Adapts RoleDefinition instances into LangChain LCEL runnables.
    """
    framework = "langchain"

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
            prompt += "\nYou have access to the following tools:\n"
            for tool in role.recommended_tools:
                prompt += f"- {tool}\n"
        prompt += "\nUse the provided tools to fulfill your responsibilities. "
        prompt += "Think step-by-step and explain your reasoning when helpful."
        return prompt

    def adapt(self, role: RoleDefinition, overlay: dict[str, Any] | None = None) -> Any:
        """
        Adapt a RoleDefinition into a LangChain LCEL runnable.
        Returns a chain that can be invoked with {"input": "..."}.
        """
        system_prompt = self.build_system_prompt(role)

        # Build a ChatPromptTemplate
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="chat_history", optional=True),
                ("human", "{input}"),
            ]
        )

        llm = self.runtime_context.llm
        tools = self.runtime_context.tools or []

        # If tools are provided, bind them to the LLM
        if tools:
            llm = llm.bind_tools(tools)

        # Create a simple chain: prompt | llm
        chain = prompt | llm
        return chain
