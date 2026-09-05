#!/usr/bin/env python3
"""Scan bounded staged and working-tree postimages without exposing secrets."""

import os
import re
import subprocess
import sys
from pathlib import Path

from engineering import changed_paths, staged_paths


def add_content(data, content):
    if len(content) > 2_000_000 or b"\0" in content:
        raise ValueError("binary or oversized postimage requires explicit review")
    try:
        content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("non-text postimage requires explicit review") from exc
    data.extend(b"\n" + content)
    if len(data) > 20_000_000:
        raise ValueError(
            "change exceeds bounded scan budget; split or review explicitly"
        )


def index_postimage(relative):
    records = subprocess.check_output(
        ["git", "--literal-pathspecs", "ls-files", "--stage", "-z", "--", relative]
    ).split(b"\0")
    entries = [record for record in records if record]
    if not entries:
        return b""  # Staged deletion.
    if len(entries) != 1:
        raise ValueError("unmerged index requires resolution before verification")
    mode, oid, stage = entries[0].split(b"\t", 1)[0].split()
    if mode not in (b"100644", b"100755") or stage != b"0":
        raise ValueError("non-regular staged postimage requires explicit review")
    size = int(subprocess.check_output(["git", "cat-file", "-s", os.fsdecode(oid)]))
    if size > 2_000_000:
        raise ValueError("oversized staged postimage requires explicit review")
    return subprocess.check_output(["git", "cat-file", "blob", os.fsdecode(oid)])


def main():
    root = Path.cwd()
    base = os.environ.get("VERIFY_BASE", "HEAD")
    try:
        paths, staged = changed_paths(root, base), staged_paths(root)
        data = bytearray()
        for relative in paths:
            if re.search(
                r"(^|/)(\.env|credentials|secrets)|\.(pem|key|p12|pfx|db|dump)$",
                relative,
                re.IGNORECASE,
            ):
                raise ValueError("sensitive path needs a dedicated authorized review")
            if relative in staged:
                add_content(data, index_postimage(relative))
            path = root / relative
            if path.is_symlink() or any(
                parent.is_symlink()
                for parent in path.parents
                if parent != root and parent.is_relative_to(root)
            ):
                raise ValueError("symlink postimage requires explicit review")
            if not path.exists():
                continue
            if (
                not path.resolve().is_relative_to(root)
                or not path.is_file()
                or path.stat().st_size > 2_000_000
            ):
                raise ValueError(
                    "non-regular or oversized postimage requires explicit review"
                )
            with path.open("rb") as stream:
                add_content(data, stream.read(2_000_001))
        return subprocess.run(
            ["gitleaks", "stdin", "--redact", "--no-banner", "--log-level", "warn"],
            input=bytes(data),
            check=False,
        ).returncode
    except ValueError as exc:
        print(f"secret check: {exc}", file=sys.stderr)
        return 1
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"secret check unavailable: {type(exc).__name__}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
