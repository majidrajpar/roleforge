"""
Restore the paid RoleForge catalog from git history into the local (non-repo) catalog dir.

The 28 paid role YAMLs and 56 overlays were removed from the working tree in commit
70fb922 (store-bundle restructure). This script re-extracts them from the repo's git
blobs (ref 70fb922^) so they remain available for personal use without living in the
public repo.

Idempotent: safe to re-run any time (overwrites the local copy with the canonical
git content).

Usage:
    uv run python tools/restore_paid_roles.py [--dest ~/.config/opencode/roleforge] [--dry-run]
"""
from __future__ import annotations

import argparse
import io
import subprocess
import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent  # repo root (parent of roleforge/)
ROLEFORGE_DIR = Path(__file__).parent.parent

# Commit whose tree contains the full 31-role catalog (paid roles deleted in 70fb922).
SOURCE_REF = "70fb922^"

# Role ids that ship free in the repo — excluded from the local paid catalog.
FREE_IDS = {"data_scientist", "ethics_advisor", "narrative_architect"}

DEFAULT_DEST = Path.home() / ".config" / "opencode" / "roleforge"

TAR_PREFIXES = ("roleforge/roles/", "roleforge/overlays/")


def archive_bytes(ref: str) -> bytes:
    """Return the git archive (tar) for roles+overlays at a given ref."""
    result = subprocess.run(
        ["git", "-C", str(ROOT), "archive", "--format=tar", ref, "roleforge/roles", "roleforge/overlays"],
        capture_output=True,
        check=True,
    )
    return result.stdout


def member_target(member_path: str, dest: Path) -> Path | None:
    """Map a tar member (roleforge/roles/... or roleforge/overlays/...) to dest/<section>/..."""
    for prefix in TAR_PREFIXES:
        if member_path.startswith(prefix):
            rel = member_path[len("roleforge/"):]  # keep the roles/ or overlays/ section
            parts = Path(rel).parts
            if len(parts) < 3:
                return None  # top-level dir entries
            role_id = Path(parts[-1]).stem
            if role_id in FREE_IDS:
                return None  # free role, lives in the repo
            return dest / rel
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Restore the paid RoleForge catalog from git history.")
    parser.add_argument("--dest", type=Path, default=DEFAULT_DEST, help="Destination catalog dir")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be written")
    parser.add_argument("--ref", default=SOURCE_REF, help="Git ref to extract from")
    args = parser.parse_args()

    dest = args.dest.resolve()
    data = archive_bytes(args.ref)

    written = 0
    skipped = 0
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:") as tar:
        members = [m for m in tar.getmembers() if m.isfile() and m.name.endswith((".yaml", ".yml"))]
        for member in members:
            target = member_target(member.name, dest)
            if target is None:
                skipped += 1
                continue
            if args.dry_run:
                print(f"[dry-run] would write {target}")
                written += 1
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            extracted = tar.extractfile(member)
            if extracted is None:
                continue
            target.write_bytes(extracted.read())
            written += 1

    roles = sorted(p.stem for p in dest.joinpath("roles").glob("*/*.yaml"))
    overlays = list(dest.joinpath("overlays").glob("*/*.yaml"))
    print(f"Source ref:          {args.ref}")
    print(f"Destination:         {dest}")
    print(f"Wrote:               {written} files ({'dry-run' if args.dry_run else 'written'})")
    print(f"Skipped (free):      {skipped} files")
    print(f"Paid roles present:  {len(roles)}")
    print(f"Overlays present:    {len(overlays)}")


if __name__ == "__main__":
    main()
