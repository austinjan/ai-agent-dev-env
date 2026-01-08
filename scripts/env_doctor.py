#!/usr/bin/env python3
"""
env_doctor.py - Validate AI agent dev environment criteria (WSL/Linux/macOS side)

CLI names (standardized):
- Claude Code   -> claude
- OpenAI Codex  -> codex
- Gemini CLI    -> gemini
"""

from __future__ import annotations

import argparse
import os
import platform
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from typing import Optional, Tuple, List


@dataclass
class CheckResult:
    name: str
    ok: bool
    details: str = ""
    fix: str = ""
    required: bool = True


def run(cmd: List[str], timeout: int = 5) -> Tuple[int, str, str]:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout.strip(), p.stderr.strip()
    except FileNotFoundError:
        return 127, "", f"not found: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"


def which(bin_name: str) -> Optional[str]:
    return shutil.which(bin_name)


def is_wsl() -> bool:
    if os.environ.get("WSL_DISTRO_NAME"):
        return True
    try:
        with open("/proc/version", "r", encoding="utf-8") as f:
            return "microsoft" in f.read().lower()
    except Exception:
        return False


def is_windows_native() -> bool:
    return platform.system().lower() == "windows"


def is_macos() -> bool:
    return platform.system().lower() == "darwin"


def is_linux() -> bool:
    return platform.system().lower() == "linux"


def project_is_on_linux_fs(project_path: str) -> bool:
    p = os.path.abspath(project_path)
    return not re.match(r"^/mnt/[a-zA-Z]/", p)


def path_contains_windows_bins() -> List[str]:
    path = os.environ.get("PATH", "")
    patterns = [
        r"/mnt/c/Program Files/nodejs",
        r"/mnt/c/Program Files \(x86\)/nodejs",
        r"/mnt/c/Users/[^/]+/AppData/Roaming/npm",
        r"/mnt/c/Users/[^/]+/AppData/Local/Microsoft/WindowsApps",
        r"/mnt/c/Users/[^/]+/AppData/Local/Programs/Python",
    ]
    return [p for p in patterns if re.search(p, path, re.IGNORECASE)]


def check_os() -> CheckResult:
    if is_windows_native():
        return CheckResult(
            name="OS is Linux / WSL / macOS (not Windows-native)",
            ok=False,
            details=f"Detected: {platform.system()}",
            fix="Run this script inside WSL/Linux/macOS terminal.",
            required=True,
        )

    kind = "WSL" if is_wsl() else ("macOS" if is_macos() else "Linux")
    return CheckResult(
        name="OS is Linux / WSL / macOS (not Windows-native)",
        ok=True,
        details=f"Detected: {kind}",
        required=True,
    )


def check_project_path(project_path: str) -> CheckResult:
    ok = project_is_on_linux_fs(project_path)
    p = os.path.abspath(project_path)
    return CheckResult(
        name="Project directory is on Linux filesystem (not /mnt/c)",
        ok=ok,
        details=p,
        fix="Move project into Linux FS (e.g. /home/<user>/project).",
        required=True,
    )


def check_python_version() -> CheckResult:
    ok = (sys.version_info.major, sys.version_info.minor) >= (3, 10)
    details = f"{sys.version.split()[0]} ({sys.executable})"
    return CheckResult(
        name="Python version >= 3.10",
        ok=ok,
        details=details,
        fix="Install Python 3.10+ and activate the correct uv venv.",
        required=True,
    )


def check_bin(name: str, required: bool, label: str) -> CheckResult:
    p = which(name)
    ok = p is not None
    return CheckResult(
        name=f"{label} is installed",
        ok=ok,
        details=p or "not found",
        fix=f"Install `{label}` in WSL/Linux/macOS and ensure it is on PATH.",
        required=required,
    )


def check_node_nvm(strict: bool) -> CheckResult:
    node = which("node")
    ok = bool(node and ".nvm" in node)
    return CheckResult(
        name="Node.js is installed via nvm",
        ok=ok,
        details=node or "node not found",
        fix="Install Node.js via nvm and run `nvm use`.",
        required=strict,
    )


def check_windows_path_hygiene(strict: bool) -> CheckResult:
    hits = path_contains_windows_bins()
    ok = len(hits) == 0
    return CheckResult(
        name="WSL PATH does not include Windows Node/Python locations",
        ok=ok,
        details="clean" if ok else f"matches: {hits}",
        fix="Remove Windows runtime paths from WSL PATH (~/.bashrc, ~/.zshrc).",
        required=strict,
    )


def print_results(results: List[CheckResult]) -> int:
    failed_required = [r for r in results if r.required and not r.ok]
    failed_optional = [r for r in results if not r.required and not r.ok]

    for r in results:
        status = "✅" if r.ok else "❌"
        req = "REQUIRED" if r.required else "OPTIONAL"
        print(f"{status} [{req}] {r.name}")
        if r.details:
            print(f"    - {r.details}")
        if not r.ok:
            print(f"    - Fix: {r.fix}")
        print()

    if failed_required:
        print(f"❌ Environment check FAILED ({len(failed_required)} required issue(s))")
        return 1

    if failed_optional:
        print(f"⚠️ Environment check PASSED with warnings ({len(failed_optional)})")
        return 0

    print("✅ Environment check PASSED")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default=os.getcwd())
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    checks = [
        check_os(),
        check_project_path(args.project),
        check_python_version(),
        check_bin("node", True, "Node.js"),
        check_bin("uv", True, "uv"),
        check_bin("gh", True, "GitHub CLI (gh)"),
        check_bin("claude", False, "Claude Code (claude)"),
        check_bin("codex", False, "OpenAI Codex (codex)"),
        check_bin("gemini", False, "Gemini CLI (gemini)"),
        check_node_nvm(args.strict),
        check_windows_path_hygiene(args.strict),
    ]

    return print_results(checks)


if __name__ == "__main__":
    raise SystemExit(main())
