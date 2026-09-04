#!/usr/bin/env python3
"""No privilege escalation: map the publisher's fixed web root to a test sandbox."""

import os
import subprocess
import sys
from pathlib import Path

root = Path(os.environ["GRAPH_PUBLISH_TEST_ROOT"])
args = sys.argv[1:]
if args[0] == "-n":
    args = args[1:]
command, *args = args
if command == "true":
    sys.exit(0)
if Path(command).name == "nginx":
    sys.exit(1 if os.environ.get("GRAPH_PUBLISH_FAIL_VALIDATE") else 0)
if command == "systemctl":
    counter = root / "reload-count"
    count = int(counter.read_text()) if counter.exists() else 0
    counter.write_text(str(count + 1))
    sys.exit(1 if count == 0 and os.environ.get("GRAPH_PUBLISH_FAIL_RELOAD") else 0)
if command not in {"install", "mkdir", "rsync", "readlink", "ln", "mv", "unlink"}:
    raise RuntimeError("Unexpected test command")
args = [
    arg.replace("/var/www/graph.kolodahearthstone.com", str(root / "web"))
    for arg in args
]
if command == "install":
    for option in ("-o", "-g"):
        if option in args:
            index = args.index(option)
            del args[index : index + 2]
if command == "rsync":
    args = [arg for arg in args if not arg.startswith("--chown=")]
result = subprocess.run([command, *args], check=False)
if command == "rsync" and os.environ.get("GRAPH_PUBLISH_TAMPER"):
    (Path(args[-1]) / "app.js").write_text("/* changed while copying */")
sys.exit(result.returncode)
