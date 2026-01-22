#!/usr/bin/env python3
"""
OAF Import Utility

Imports and validates an OAF package (.oaf file).
This is a local utility for testing - in production, use the API.
"""

import argparse
import json
import os
import shutil
import sys
import zipfile
from pathlib import Path

import yaml


def validate_oaf_package(oaf_path: Path) -> dict:
    """Validate and extract metadata from an OAF package."""

    if not oaf_path.exists():
        raise FileNotFoundError(f"Package not found: {oaf_path}")

    if not zipfile.is_zipfile(oaf_path):
        raise ValueError(f"Not a valid ZIP file: {oaf_path}")

    result = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "package": None,
        "agents": [],
    }

    with zipfile.ZipFile(oaf_path, "r") as zf:
        names = zf.namelist()

        # Check for PACKAGE.yaml
        if "PACKAGE.yaml" not in names:
            result["warnings"].append("Missing PACKAGE.yaml at root (optional but recommended)")
        else:
            package_content = zf.read("PACKAGE.yaml").decode("utf-8")
            result["package"] = yaml.safe_load(package_content)

        # Find all AGENTS.md files
        agents_md_files = [n for n in names if n.endswith("AGENTS.md")]

        if not agents_md_files:
            result["valid"] = False
            result["errors"].append("No AGENTS.md found in package")
            return result

        # Validate each agent
        for agents_md in agents_md_files:
            agent_dir = str(Path(agents_md).parent)
            content = zf.read(agents_md).decode("utf-8")

            # Parse frontmatter
            if not content.startswith("---"):
                result["errors"].append(f"{agents_md}: Missing YAML frontmatter")
                continue

            end_idx = content.find("---", 3)
            if end_idx == -1:
                result["errors"].append(f"{agents_md}: Frontmatter not properly closed")
                continue

            frontmatter = content[3:end_idx].strip()
            try:
                metadata = yaml.safe_load(frontmatter)
            except yaml.YAMLError as e:
                result["errors"].append(f"{agents_md}: Invalid YAML: {e}")
                continue

            # Check required OAF fields
            required = ["name", "vendorKey", "agentKey", "version", "slug",
                       "description", "author", "license", "tags"]
            missing = [f for f in required if f not in metadata]

            agent_info = {
                "path": agent_dir,
                "metadata": metadata,
                "missing_fields": missing,
                "skills": [],
            }

            if missing:
                result["warnings"].append(
                    f"{agents_md}: Missing OAF fields: {', '.join(missing)}"
                )

            # Find skills for this agent
            skill_prefix = f"{agent_dir}/skills/" if agent_dir else "skills/"
            skill_mds = [n for n in names if n.startswith(skill_prefix) and n.endswith("SKILL.md")]

            for skill_md in skill_mds:
                skill_name = Path(skill_md).parent.name
                agent_info["skills"].append(skill_name)

            result["agents"].append(agent_info)

    if result["errors"]:
        result["valid"] = False

    return result


def import_agent(oaf_path: Path, output_dir: Path, rename_to: str | None = None) -> Path:
    """Import an OAF package to a directory."""

    print(f"Importing: {oaf_path}")
    print(f"Target: {output_dir}")
    print()

    # Validate first
    print("Validating package...")
    validation = validate_oaf_package(oaf_path)

    if validation["package"]:
        pkg = validation["package"]
        print(f"  Package: {pkg.get('name', 'N/A')}")
        print(f"  Version: {pkg.get('version', 'N/A')}")
        print(f"  Contents mode: {pkg.get('contents_mode', 'N/A')}")
        print(f"  Created: {pkg.get('created_at', 'N/A')}")

    print()
    print(f"Found {len(validation['agents'])} agent(s):")

    for agent in validation["agents"]:
        meta = agent["metadata"]
        print(f"\n  Agent: {meta.get('name', 'Unknown')}")
        print(f"    vendorKey: {meta.get('vendorKey', 'N/A')}")
        print(f"    agentKey: {meta.get('agentKey', 'N/A')}")
        print(f"    version: {meta.get('version', 'N/A')}")
        print(f"    author: {meta.get('author', 'N/A')}")
        print(f"    license: {meta.get('license', 'N/A')}")
        print(f"    skills: {len(agent['skills'])} ({', '.join(agent['skills'])})")

        if agent["missing_fields"]:
            print(f"    [!] Missing fields: {', '.join(agent['missing_fields'])}")

    if validation["errors"]:
        print("\n[ERROR] Validation failed:")
        for err in validation["errors"]:
            print(f"  - {err}")
        raise ValueError("Package validation failed")

    if validation["warnings"]:
        print("\n[WARN] Warnings:")
        for warn in validation["warnings"]:
            print(f"  - {warn}")

    # Extract the package
    print("\nExtracting package...")

    # Determine output directory name
    if rename_to:
        agent_dir_name = rename_to
    elif validation["agents"]:
        agent_dir_name = validation["agents"][0]["metadata"].get("agentKey", "imported-agent")
    else:
        agent_dir_name = oaf_path.stem

    extract_path = output_dir / agent_dir_name

    if extract_path.exists():
        print(f"  [!] Directory exists, removing: {extract_path}")
        shutil.rmtree(extract_path)

    with zipfile.ZipFile(oaf_path, "r") as zf:
        # Extract all files
        for member in zf.namelist():
            # Skip PACKAGE.yaml at root (it's package metadata, not agent content)
            if member == "PACKAGE.yaml":
                continue

            # Determine target path (flatten if there's a wrapper directory)
            member_path = Path(member)
            parts = member_path.parts

            # If first part is "package" or similar wrapper, skip it
            if parts and parts[0] in ("package", agent_dir_name):
                target_rel = Path(*parts[1:]) if len(parts) > 1 else Path()
            else:
                target_rel = member_path

            if not target_rel.parts:
                continue

            target_path = extract_path / target_rel

            if member.endswith("/"):
                target_path.mkdir(parents=True, exist_ok=True)
            else:
                target_path.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(member) as src, open(target_path, "wb") as dst:
                    dst.write(src.read())

    # Count extracted files
    file_count = sum(1 for _ in extract_path.rglob("*") if _.is_file())

    print(f"  Extracted {file_count} files to: {extract_path}")

    # Verify AGENTS.md exists
    agents_md = extract_path / "AGENTS.md"
    if agents_md.exists():
        print(f"\n[OK] Import successful!")
        print(f"  Agent location: {extract_path}")
        print(f"  AGENTS.md: {agents_md}")
    else:
        print(f"\n[WARN] AGENTS.md not at expected location")

    return extract_path


def main():
    parser = argparse.ArgumentParser(
        description="Import and validate an OAF package (.oaf file)"
    )
    parser.add_argument(
        "oaf_file",
        type=Path,
        help="Path to the .oaf file to import"
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=Path("."),
        help="Output directory (default: current directory)"
    )
    parser.add_argument(
        "--rename",
        type=str,
        help="Rename the agent directory on import"
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate, don't extract"
    )

    args = parser.parse_args()

    if not args.oaf_file.exists():
        print(f"Error: File not found: {args.oaf_file}", file=sys.stderr)
        sys.exit(1)

    try:
        if args.validate_only:
            result = validate_oaf_package(args.oaf_file)
            print(f"Package: {args.oaf_file}")
            print(f"Valid: {result['valid']}")
            if result["errors"]:
                print("Errors:")
                for e in result["errors"]:
                    print(f"  - {e}")
            if result["warnings"]:
                print("Warnings:")
                for w in result["warnings"]:
                    print(f"  - {w}")
            sys.exit(0 if result["valid"] else 1)
        else:
            import_agent(args.oaf_file, args.output, args.rename)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
