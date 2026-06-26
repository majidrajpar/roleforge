"""
Validation script for all 31 roles in the library.
Runs deterministic validators and reports any issues.
"""
from __future__ import annotations

import sys
from pathlib import Path

src_path = str(Path(__file__).parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from loader import RoleLoader, RoleRegistry
from validators import RoleValidator, ValidationError


def main():
    print("=" * 60)
    print("AGENT ROLES LIBRARY - VALIDATION REPORT")
    print("=" * 60)
    print()

    # Load all roles
    registry = RoleRegistry()
    registry.index()
    roles = registry.list_roles()

    print(f"Total roles loaded: {len(roles)}")
    print()

    # Validate each role individually
    validator = RoleValidator(roles)
    all_errors = validator.validate_registry()

    if not all_errors:
        print("✅ All roles passed validation!")
        print()
    else:
        print(f"❌ Found {len(all_errors)} validation issue(s):")
        for error in all_errors:
            print(f"  - {error}")
        print()

    # Summary by category
    from collections import Counter
    categories = Counter(r.category for r in roles)
    print("Roles by category:")
    for category, count in sorted(categories.items()):
        print(f"  {category}: {count}")
    print()

    # Overlay coverage
    overlay_count = len(registry._overlays)
    print(f"Framework overlays: {overlay_count}")
    if overlay_count > 0:
        frameworks = set(k[0] for k in registry._overlays.keys())
        for fw in frameworks:
            fw_overlays = [k[1] for k in registry._overlays.keys() if k[0] == fw]
            print(f"  {fw}: {len(fw_overlays)} overlay(s) for {', '.join(fw_overlays)}")
    print()

    print("=" * 60)
    print("VALIDATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
