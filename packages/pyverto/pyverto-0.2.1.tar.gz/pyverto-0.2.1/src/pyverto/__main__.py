#!/usr/bin/env python
# SPDX-FileCopyrightText: 2025-present phdenzel <phdenzel@gmail.com>
# SPDX-FileNotice: Part of pyverto
# SPDX-License-Identifier: MIT
"""Version management for any Python project.

Usage:
  pyverto [command] [--commit]

Commands:
  version    Print out current version
  release    Remove any pre-release/dev/post suffix (finalize version)
  major      Increment the major version
  minor      Increment the minor version
  micro      Increment the micro (patch) version
  alpha      Convert to or increment alpha pre-release
  beta       Convert to or increment beta pre-release
  pre        Convert to or increment rc (release candidate)
  rev        Increment post-release (+postN)
  dev        Convert to or increment dev release (-devN)

Examples:
  pyverto dev
  pyverto pre --commit
"""

import argparse
from pathlib import Path
from pyverto.utils import (
    find_version_file,
    get_current_version,
    write_version,
    parse_version,
    format_version,
)
from pyverto.vc import git_commit_and_tag
from pyverto.header import get_project_name, generate_default_header, insert_header


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Version incrementor.")
    parser.add_argument(
        "command",
        choices=[
            "version",
            "release",
            "major",
            "minor",
            "micro",
            "alpha",
            "beta",
            "pre",
            "rev",
            "dev",
            "header",
        ],
        help="Version bump type",
    )
    parser.add_argument(
        "-n", "--dry-run", action="store_true", help="Dry-run, i.e. no changes are applied."
    )
    parser.add_argument("--commit", action="store_true", help="Commit & tag in git")
    parser.add_argument("--no-tag", action="store_true", help="Do not tag when committing")
    parser.add_argument(
        "--header-file",
        "--hdr-file",
        type=Path,
        help="Optional file containing a custom header to insert into project files.",
    )
    parser.add_argument(
        "--header-text",
        "--header-txt",
        "--hdr-txt",
        type=str,
        help="Optional text containing a custom header to insert into project files.",
    )
    parser.add_argument(
        "-d",
        "--target-dirs",
        "--targets",
        action="append",
        type=Path,
        default=["{project_name}", Path("src")],
        help="Project directories where to look for python files",
    )

    args = parser.parse_args()
    print(args)
    return args


def bump(command: str, current_version: str):
    """Bump version in various ways.

    Args:
        command: The manner how the version is incremented.
        current_version: Version string to be incremented.
    """
    major, minor, micro, label, num, post, pre_sep, post_sep = parse_version(current_version)
    if command == "version":
        return format_version(
            major,
            minor,
            micro,
            label,
            num,
            post,
            pre_separator=pre_sep,
            post_separator=post_sep,
        )
    if command == "release":
        return format_version(major, minor, micro)
    if command == "major":
        return format_version(major + 1, 0, 0)
    if command == "minor":
        return format_version(major, minor + 1, 0)
    if command in ("micro", "patch"):
        return format_version(major, minor, micro + 1)
    if command in ("alpha", "beta", "pre"):
        stage = {"pre": "rc"}.get(command, command)
        if label == stage:
            num = (num or 0) + 1
        else:
            num = 0
        return format_version(
            major,
            minor,
            micro,
            stage,
            num,
            pre_separator=pre_sep
            if any([k in current_version for k in ["alpha", "beta", "pre", "rc"]])
            else ".",
        )
    if command == "rev":
        return format_version(
            major,
            minor,
            micro,
            label,
            num,
            (post or 0) + 1,
            pre_separator=pre_sep,
            post_separator=post_sep if post else "-",
        )
    if command == "dev":
        if label == "dev":
            num = (num or 0) + 1
        else:
            num = 0
        return format_version(
            major,
            minor,
            micro,
            "dev",
            num,
            pre_separator=pre_sep if "dev" in current_version else ".",
        )
    raise ValueError(f"Unknown command: {command}")


def edit_header(
    header_file: Path | None = None,
    header_text: str | None = None,
    target_dirs: list[Path | str] = ["src"],
    dry_run: bool = False,
):
    """Edit header of project files."""
    pyproject = Path("pyproject.toml")
    if header_file is not None:
        header_text = header_file.read_text().strip()
    elif header_text is not None:
        header_text = header_text.strip()
    else:
        if not pyproject.exists():
            raise SystemExit(
                "pyproject.toml not found. "
                "Use --header-file or --header-text flags to edit headers."
            )
        header_text = generate_default_header(pyproject)
    project_name = get_project_name(pyproject.parent).replace("-", "_")
    target_dirs = [
        Path(p.format(project_name=project_name)) if p == "{project_name}" else p
        for p in target_dirs
    ]
    target_files = [f for d in target_dirs for f in d.rglob("**/*.py")]
    for py_file in target_files:
        if py_file.name.startswith("."):
            continue
        if dry_run:
            print(py_file)
            print(header_text)
        else:
            insert_header(py_file, header_text)


def main():
    """Main entry point."""
    args = parse_args()
    version_file = find_version_file()
    if not version_file:
        raise SystemExit("Error: Could not locate a file with __version__.")
    current_version = get_current_version(version_file)
    if args.command == "header":
        edit_header(args.header_file, target_dirs=args.target_dirs, dry_run=args.dry_run)
    elif args.command == "version":
        print(current_version)
    else:
        new_version = bump(args.command, current_version)
        if not args.dry_run:
            write_version(version_file, new_version)
        print(f"Bumped version in {version_file}: {current_version} → {new_version}")
        if args.commit and not args.dry_run:
            git_commit_and_tag(version_file, new_version, current_version, tag=(not args.no_tag))


if __name__ == "__main__":
    main()
