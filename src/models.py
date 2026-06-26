"""
Pydantic models for the Agent Roles Library.
"""
from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field, field_validator


class RoleDefinition(BaseModel):
    """
    Framework-agnostic representation of an agent role.
    """
    id: str = Field(..., description="Unique snake_case identifier")
    name: str = Field(..., description="Human-readable role name")
    category: str = Field(..., description="Category slug (e.g., risk_management)")
    domain_tags: list[str] = Field(default_factory=list, description="Domain keywords")
    description: str = Field(..., min_length=50, description="Role description")
    responsibilities: list[str] = Field(..., min_length=1, description="List of responsibilities")
    expertise: list[str] = Field(..., min_length=1, description="Areas of expertise")
    recommended_tools: list[str] = Field(default_factory=list, description="Optional tool recommendations")

    @field_validator("id")
    @classmethod
    def validate_id_snake_case(cls, v: str) -> str:
        if not v.replace("_", "").isalnum():
            raise ValueError("id must be snake_case alphanumeric")
        return v

    @field_validator("description")
    @classmethod
    def validate_description_length(cls, v: str) -> str:
        if len(v.strip()) < 50:
            raise ValueError("description must be at least 50 characters")
        return v

    @field_validator("responsibilities")
    @classmethod
    def validate_responsibilities(cls, v: list[str]) -> list[str]:
        if len(v) < 1:
            raise ValueError("at least 1 responsibility required")
        return v

    @field_validator("expertise")
    @classmethod
    def validate_expertise(cls, v: list[str]) -> list[str]:
        if len(v) < 1:
            raise ValueError("at least 1 expertise item required")
        return v


class RuntimeContext(BaseModel):
    """
    Framework-specific runtime context supplied to adapters.
    Adapters consume a RoleDefinition + RuntimeContext.
    """
    llm: Any = Field(..., description="LLM instance or model identifier")
    tools: list[Any] = Field(default_factory=list, description="List of tool instances")
    memory: Any | None = Field(default=None, description="Memory instance")
    # LangGraph-specific
    state_schema: type | None = Field(default=None, description="TypedDict / dataclass for graph state")
    # CrewAI-specific
    allow_delegation: bool = Field(default=True, description="Allow agent delegation")
    # LangChain-specific
    agent_type: str | None = Field(default=None, description="Agent type identifier")

    class Config:
        arbitrary_types_allowed = True


class Overlay(BaseModel):
    """
    Generic overlay for framework-specific overrides.
    """
    framework: str = Field(..., description="Framework identifier (e.g., crewai)")
    role_id: str = Field(..., description="Target role id")
    data: dict[str, Any] = Field(default_factory=dict, description="Framework-specific key-value overrides")
