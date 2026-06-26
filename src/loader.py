"""
YAML loader and registry for role definitions.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Iterator

import yaml

from models import RoleDefinition, Overlay
from validators import RoleValidator, ValidationError


DEFAULT_ROLES_DIR = Path(__file__).parent.parent / "roles"
DEFAULT_SCHEMA_PATH = Path(__file__).parent.parent / "schemas" / "role.schema.json"


class RoleLoader:
    """
    Loads and validates role YAML files into RoleDefinition instances.
    """

    def __init__(self, roles_dir: Path | str | None = None, schema_path: Path | str | None = None):
        self.roles_dir = Path(roles_dir or DEFAULT_ROLES_DIR)
        self.schema_path = Path(schema_path or DEFAULT_SCHEMA_PATH)
        self._schema: dict | None = None

    def _load_schema(self) -> dict:
        if self._schema is None:
            with open(self.schema_path, "r", encoding="utf-8") as f:
                self._schema = json.load(f)
        return self._schema

    def load_role(self, path: Path | str) -> RoleDefinition:
        """Load a single role YAML file."""
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        role = RoleDefinition.model_validate(data)
        return role

    def load_all(self) -> list[RoleDefinition]:
        """Load all role YAML files from the roles directory."""
        roles: list[RoleDefinition] = []
        if not self.roles_dir.exists():
            return roles
        for file_path in sorted(self.roles_dir.rglob("*.yaml")):
            roles.append(self.load_role(file_path))
        return roles

    def load_overlay(self, framework: str, role_id: str, overlays_dir: Path | str | None = None) -> Overlay | None:
        """Load a framework-specific overlay for a role."""
        overlays_dir = Path(overlays_dir or Path(__file__).parent.parent / "overlays")
        overlay_path = overlays_dir / framework / f"{role_id}.yaml"
        if not overlay_path.exists():
            return None
        with open(overlay_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return Overlay(framework=framework, role_id=role_id, data=data or {})


class RoleRegistry:
    """
    In-memory registry for discovering and querying roles.
    """

    def __init__(self, loader: RoleLoader | None = None):
        self.loader = loader or RoleLoader()
        self._roles: dict[str, RoleDefinition] = {}
        self._overlays: dict[tuple[str, str], Overlay] = {}

    def index(self) -> None:
        """Index all roles and overlays."""
        self._roles = {}
        self._overlays = {}
        for role in self.loader.load_all():
            self._roles[role.id] = role
        # Index overlays
        overlays_dir = Path(__file__).parent.parent / "overlays"
        if overlays_dir.exists():
            for framework_dir in overlays_dir.iterdir():
                if framework_dir.is_dir():
                    for overlay_file in framework_dir.glob("*.yaml"):
                        role_id = overlay_file.stem
                        overlay = self.loader.load_overlay(framework_dir.name, role_id, overlays_dir)
                        if overlay:
                            self._overlays[(framework_dir.name, role_id)] = overlay

    def get(self, role_id: str) -> RoleDefinition | None:
        """Retrieve a role by id."""
        return self._roles.get(role_id)

    def list_roles(self) -> list[RoleDefinition]:
        """List all indexed roles."""
        return list(self._roles.values())

    def search(self, query: str) -> list[RoleDefinition]:
        """Search roles by name, category, or tags (case-insensitive)."""
        q = query.lower()
        results: list[RoleDefinition] = []
        for role in self._roles.values():
            if (
                q in role.name.lower()
                or q in role.category.lower()
                or any(q in tag.lower() for tag in role.domain_tags)
                or q in role.description.lower()
            ):
                results.append(role)
        return results

    def get_overlay(self, framework: str, role_id: str) -> Overlay | None:
        """Retrieve an overlay for a role."""
        return self._overlays.get((framework, role_id))

    def get_role_with_overlay(self, role_id: str, framework: str | None = None) -> tuple[RoleDefinition, Overlay | None]:
        """Retrieve a role and optional overlay."""
        role = self.get(role_id)
        if role is None:
            raise KeyError(f"Role '{role_id}' not found")
        overlay = self.get_overlay(framework, role_id) if framework else None
        return role, overlay
