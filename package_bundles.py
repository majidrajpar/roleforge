"""
Package RoleForge product bundles for Gumroad upload.

Run this script to generate ZIP files for each pricing tier.
Usage: python package_bundles.py
"""
from pathlib import Path
import zipfile
import shutil

REPO_ROOT = Path(__file__).parent
OUTPUT_DIR = REPO_ROOT / "gumroad_bundles"
ROLES_DIR = REPO_ROOT / "roles"
OVERLAYS_DIR = REPO_ROOT / "overlays"

def create_bundle(name: str, role_files: list[Path], extra_files: dict[str, str] = None):
    """Create a ZIP bundle with roles, overlays, and a README."""
    bundle_dir = OUTPUT_DIR / name
    if bundle_dir.exists():
        shutil.rmtree(bundle_dir)
    bundle_dir.mkdir(parents=True)
    
    # Copy role files
    for role_file in role_files:
        shutil.copy2(role_file, bundle_dir / role_file.name)
        # Copy overlays
        role_id = role_file.stem
        for framework in ["crewai", "langgraph"]:
            overlay = OVERLAYS_DIR / framework / f"{role_id}.yaml"
            if overlay.exists():
                shutil.copy2(overlay, bundle_dir / f"{role_id}.{framework}.yaml")
    
    # Create bundle README
    readme = bundle_dir / "README.md"
    readme.write_text(f"""# {name.replace('_', ' ').title()}

**One-time purchase. Lifetime access.**

## Contents

This bundle includes {len(role_files)} production-grade agent roles with framework overlays.

## How to Use

1. Install RoleForge:
   ```bash
   pip install roleforge
   ```

2. Load a role:
   ```python
   from roleforge import RoleRegistry
   registry = RoleRegistry()
   registry.index()
   role = registry.get("lead_internal_auditor")
   ```

3. Adapt to your framework:
   ```python
   from roleforge.adapters.crewai_adapter import CrewAIAdapter
   agent = CrewAIAdapter(context).adapt(role)
   ```

## Support

- GitHub: https://github.com/majidrajpar/roleforge
- Email: majidrajpar@gmail.com

## License

These roles are licensed under the Elastic License 2.0.
Free for personal, educational, and internal business use.
Commercial redistribution requires an Enterprise License.
See COMMERCIAL_LICENSE.md for details.
""")
    
    # Create ZIP
    zip_path = OUTPUT_DIR / f"{name}.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file in bundle_dir.iterdir():
            zf.write(file, arcname=file.name)
    
    print(f"✓ Created {zip_path.name} ({zip_path.stat().st_size} bytes, {len(role_files)} roles)")
    return zip_path


def main():
    print("=" * 60)
    print("PACKAGING ROLEFORGE BUNDLES FOR GUMROAD")
    print("=" * 60)
    print()
    
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Get all role files
    all_roles = sorted(ROLES_DIR.rglob("*.yaml"))
    print(f"Found {len(all_roles)} roles total")
    print()
    
    # Domain packs
    domains = {
        "audit_domain_pack": list((ROLES_DIR / "audit").glob("*.yaml")),
        "risk_domain_pack": list((ROLES_DIR / "risk").glob("*.yaml")),
        "governance_domain_pack": list((ROLES_DIR / "governance").glob("*.yaml")),
        "philosophy_domain_pack": list((ROLES_DIR / "philosophy").glob("*.yaml")),
        "creative_writing_domain_pack": list((ROLES_DIR / "creative_writing").glob("*.yaml")),
        "book_writing_domain_pack": list((ROLES_DIR / "book_writing").glob("*.yaml")),
        "data_analysis_domain_pack": list((ROLES_DIR / "data_analysis").glob("*.yaml")),
    }
    
    print("Domain Packs:")
    for name, roles in domains.items():
        if roles:
            create_bundle(name, roles)
    print()
    
    # Professional Pack (sample: Audit + Risk + Governance)
    professional_roles = (
        list((ROLES_DIR / "audit").glob("*.yaml")) +
        list((ROLES_DIR / "risk").glob("*.yaml")) +
        list((ROLES_DIR / "governance").glob("*.yaml"))
    )
    print("Professional Pack:")
    create_bundle("professional_pack", professional_roles)
    print()
    
    # Complete Bundle (all 31 roles)
    print("Complete Bundle:")
    create_bundle("complete_bundle", all_roles)
    print()
    
    # Enterprise Bundle (same as complete + enterprise license)
    print("Enterprise Bundle:")
    enterprise_dir = OUTPUT_DIR / "enterprise_bundle"
    if enterprise_dir.exists():
        shutil.rmtree(enterprise_dir)
    enterprise_dir.mkdir(parents=True)
    
    # Copy all roles
    for role_file in all_roles:
        shutil.copy2(role_file, enterprise_dir / role_file.name)
        role_id = role_file.stem
        for framework in ["crewai", "langgraph"]:
            overlay = OVERLAYS_DIR / framework / f"{role_id}.yaml"
            if overlay.exists():
                shutil.copy2(overlay, enterprise_dir / f"{role_id}.{framework}.yaml")
    
    # Add enterprise license file
    enterprise_license = enterprise_dir / "ENTERPRISE_LICENSE.txt"
    enterprise_license.write_text("""ROLEFORGE ENTERPRISE LICENSE

This bundle is licensed for commercial redistribution.

You may:
- Embed these roles in commercial products
- Host these roles as part of a managed service
- Modify roles for your customers
- White-label under your own branding

You may NOT:
- Resell these roles as standalone products
- Remove license headers or attribution

For questions: majidrajpar@gmail.com
""")
    
    # Create ZIP
    zip_path = OUTPUT_DIR / "enterprise_bundle.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file in enterprise_dir.iterdir():
            zf.write(file, arcname=file.name)
    
    print(f"✓ Created {zip_path.name} ({zip_path.stat().st_size} bytes, {len(all_roles)} roles + enterprise license)")
    print()
    
    # Summary
    print("=" * 60)
    print("BUNDLES READY FOR GUMROAD")
    print("=" * 60)
    for zip_file in sorted(OUTPUT_DIR.glob("*.zip")):
        size_mb = zip_file.stat().st_size / (1024 * 1024)
        print(f"  {zip_file.name:40s} {size_mb:.2f} MB")
    print()
    print("Upload these ZIPs to Gumroad. Done.")


if __name__ == "__main__":
    main()
