"""
Abstract base adapter and runtime context contract.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from models import RoleDefinition, RuntimeContext


class BaseAdapter(ABC):
    """
    Abstract base class for framework-specific adapters.

    Contract:
    - Adapters consume a validated RoleDefinition + RuntimeContext.
    - Portable: persona, system prompt, responsibilities, expertise.
    - Runtime-supplied: model, tools, memory, state schema, delegation rules.
    """

    framework: str

    def __init__(self, runtime_context: RuntimeContext):
        self.runtime_context = runtime_context

    @abstractmethod
    def build_system_prompt(self, role: RoleDefinition) -> str:
        """
        Build a framework-agnostic system prompt from the role definition.
        This is portable across all frameworks.
        """
        ...

    @abstractmethod
    def adapt(self, role: RoleDefinition, overlay: dict[str, Any] | None = None) -> Any:
        """
        Adapt a RoleDefinition into a framework-specific agent/node/runnable.
        Accepts an optional overlay dict for framework-specific overrides.
        """
        ...

    def _merge_overlay(self, role: RoleDefinition, overlay: dict[str, Any] | None) -> dict[str, Any]:
        """Helper: merge role fields with overlay data."""
        merged = {
            "id": role.id,
            "name": role.name,
            "description": role.description,
            "responsibilities": role.responsibilities,
            "expertise": role.expertise,
        }
        if overlay:
            merged.update(overlay)
        return merged
