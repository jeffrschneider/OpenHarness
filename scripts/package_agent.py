#!/usr/bin/env python3
"""
OAF Package Utility

Packages an agent directory into an OAF-compliant .oaf file.
This is a local utility for testing - in production, use the API.
"""

import argparse
import json
import os
import sys
import zipfile
from datetime import datetime
from pathlib import Path

import yaml


def parse_agents_md(agents_md_path: Path) -> dict:
    """Parse AGENTS.md frontmatter."""
    content = agents_md_path.read_text(encoding="utf-8")

    if not content.startswith("---"):
        raise ValueError("AGENTS.md must start with YAML frontmatter (---)")

    # Find the closing ---
    end_idx = content.find("---", 3)
    if end_idx == -1:
        raise ValueError("AGENTS.md frontmatter not properly closed")

    frontmatter = content[3:end_idx].strip()
    return yaml.safe_load(frontmatter)


def validate_oaf_fields(metadata: dict) -> list[str]:
    """Validate required OAF fields and return warnings."""
    warnings = []
    required = ["name", "vendorKey", "agentKey", "version", "slug", "description", "author", "license", "tags"]

    for field in required:
        if field not in metadata:
            warnings.append(f"Missing required OAF field: {field}")

    # Validate formats
    if "version" in metadata:
        parts = str(metadata["version"]).split(".")
        if len(parts) != 3:
            warnings.append(f"Version '{metadata['version']}' should be semantic (e.g., 1.0.0)")

    if "vendorKey" in metadata:
        vk = metadata["vendorKey"]
        if vk != vk.lower() or " " in vk:
            warnings.append(f"vendorKey '{vk}' should be lowercase kebab-case")

    if "agentKey" in metadata:
        ak = metadata["agentKey"]
        if ak != ak.lower() or " " in ak:
            warnings.append(f"agentKey '{ak}' should be lowercase kebab-case")

    return warnings


def create_package_yaml(metadata: dict, agent_path: Path) -> str:
    """Create PACKAGE.yaml content."""
    package = {
        "name": f"{metadata.get('vendorKey', 'unknown')}-{metadata.get('agentKey', 'agent')}-package",
        "version": metadata.get("version", "0.1.0"),
        "created_at": datetime.utcnow().isoformat() + "Z",
        "contents_mode": "bundled",
        "agents": [
            {
                "path": f"{agent_path.name}/",
                "name": metadata.get("name", agent_path.name),
                "version": metadata.get("version", "0.1.0"),
                "vendorKey": metadata.get("vendorKey"),
                "agentKey": metadata.get("agentKey"),
            }
        ]
    }
    return yaml.dump(package, default_flow_style=False, sort_keys=False)


def package_agent(agent_dir: Path, output_path: Path | None = None) -> Path:
    """Package an agent directory into an .oaf file."""

    # Validate agent directory
    agents_md = agent_dir / "AGENTS.md"
    if not agents_md.exists():
        raise FileNotFoundError(f"AGENTS.md not found in {agent_dir}")

    # Parse and validate metadata
    print(f"Reading {agents_md}...")
    metadata = parse_agents_md(agents_md)

    print(f"Agent: {metadata.get('name', 'Unknown')}")
    print(f"  vendorKey: {metadata.get('vendorKey', 'N/A')}")
    print(f"  agentKey: {metadata.get('agentKey', 'N/A')}")
    print(f"  version: {metadata.get('version', 'N/A')}")

    # Validate OAF compliance
    warnings = validate_oaf_fields(metadata)
    if warnings:
        print("\nOAF Validation Warnings:")
        for w in warnings:
            print(f"  [!] {w}")
    else:
        print("\n[OK] All required OAF fields present")

    # Determine output path
    if output_path is None:
        agent_key = metadata.get("agentKey", agent_dir.name)
        version = metadata.get("version", "0.1.0")
        output_path = agent_dir.parent / f"{agent_key}-{version}.oaf"

    # Create the .oaf package
    print(f"\nCreating package: {output_path}")

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # Add PACKAGE.yaml at root
        package_yaml = create_package_yaml(metadata, agent_dir)
        zf.writestr("PACKAGE.yaml", package_yaml)

        # Add all files from agent directory
        file_count = 0
        for root, dirs, files in os.walk(agent_dir):
            # Skip __pycache__ and hidden directories
            dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]

            for file in files:
                if file.startswith("."):
                    continue

                file_path = Path(root) / file
                arc_name = str(file_path.relative_to(agent_dir.parent))
                zf.write(file_path, arc_name)
                file_count += 1

        print(f"  Added {file_count} files")

    # Print package contents
    print(f"\nPackage contents:")
    with zipfile.ZipFile(output_path, "r") as zf:
        for info in zf.infolist():
            size = info.file_size
            print(f"  {info.filename} ({size} bytes)")

    file_size = output_path.stat().st_size
    print(f"\n[OK] Created {output_path.name} ({file_size:,} bytes)")

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Package an agent directory into an OAF-compliant .oaf file"
    )
    parser.add_argument(
        "agent_dir",
        type=Path,
        help="Path to the agent directory (containing AGENTS.md)"
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output .oaf file path (default: <agentKey>-<version>.oaf)"
    )

    args = parser.parse_args()

    if not args.agent_dir.exists():
        print(f"Error: Directory not found: {args.agent_dir}", file=sys.stderr)
        sys.exit(1)

    try:
        output = package_agent(args.agent_dir, args.output)
        print(f"\nSuccess! Package ready at: {output}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
