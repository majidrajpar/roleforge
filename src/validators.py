"""
Deterministic validators for role definitions.
"""
from __future__ import annotations

from typing import Iterator
from models import RoleDefinition


class ValidationError(Exception):
    """Raised when a role fails deterministic validation."""
    pass


class RoleValidator:
    """
    Validates RoleDefinition instances against deterministic rules.
    """

    MIN_DESCRIPTION_LENGTH = 50
    MIN_RESPONSIBILITIES = 1
    MIN_EXPERTISE = 1

    def __init__(self, registry: list[RoleDefinition] | None = None):
        self.registry = registry or []

    def validate(self, role: RoleDefinition) -> list[str]:
        """Validate a single role. Returns list of error messages (empty if valid)."""
        errors: list[str] = []

        # Description length
        if len(role.description.strip()) < self.MIN_DESCRIPTION_LENGTH:
            errors.append(
                f"[{role.id}] description too short ({len(role.description.strip())} chars, "
                f"min {self.MIN_DESCRIPTION_LENGTH})"
            )

        # Responsibilities count
        if len(role.responsibilities) < self.MIN_RESPONSIBILITIES:
            errors.append(
                f"[{role.id}] insufficient responsibilities ({len(role.responsibilities)}, "
                f"min {self.MIN_RESPONSIBILITIES})"
            )

        # Expertise count
        if len(role.expertise) < self.MIN_EXPERTISE:
            errors.append(
                f"[{role.id}] insufficient expertise items ({len(role.expertise)}, "
                f"min {self.MIN_EXPERTISE})"
            )

        # Duplicate responsibilities check
        seen: set[str] = set()
        for resp in role.responsibilities:
            normalized = resp.strip().lower()
            if normalized in seen:
                errors.append(f"[{role.id}] duplicate responsibility: {resp}")
            seen.add(normalized)

        return errors

    def validate_registry(self) -> list[str]:
        """Validate all roles in the registry, including cross-role checks."""
        all_errors: list[str] = []

        # Single-role validation
        for role in self.registry:
            all_errors.extend(self.validate(role))

        # Cross-role: overlapping responsibilities
        resp_map: dict[str, list[str]] = {}
        for role in self.registry:
            for resp in role.responsibilities:
                normalized = resp.strip().lower()
                resp_map.setdefault(normalized, []).append(role.id)

        for resp, role_ids in resp_map.items():
            if len(role_ids) > 1:
                all_errors.append(
                    f"Overlapping responsibility across roles: '{resp}' found in {role_ids}"
                )

        return all_errors

    def assert_valid(self, role: RoleDefinition) -> None:
        """Raise ValidationError if role is invalid."""
        errors = self.validate(role)
        if errors:
            raise ValidationError("; ".join(errors))
