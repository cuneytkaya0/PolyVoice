"""Validate PolyVoice's local Windows/Python prerequisites without side effects."""

from __future__ import annotations

import argparse
import ctypes
from ctypes import wintypes
import encodings
import os
from pathlib import Path
import platform
import shutil
import sys
import sysconfig
import venv


MINIMUM_FREE_BYTES = 5 * 1024**3
RECOMMENDED_RAM_BYTES = 8 * 1024**3


class _MemoryStatus(ctypes.Structure):
    _fields_ = [
        ("dwLength", wintypes.DWORD),
        ("dwMemoryLoad", wintypes.DWORD),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]


def _physical_memory() -> int | None:
    status = _MemoryStatus()
    status.dwLength = ctypes.sizeof(status)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        return None
    return status.ullTotalPhys


def check(project_root: Path, *, preflight: bool, require_venv: bool) -> int:
    problems: list[str] = []
    if sys.platform != "win32" or sys.getwindowsversion().major != 10:
        problems.append("PolyVoice requires Windows 10 or Windows 11.")
    if sys.version_info[:2] != (3, 12):
        problems.append(f"Python 3.12 is required; found {sys.version.split()[0]}.")
    if platform.architecture()[0] != "64bit" or platform.machine().lower() not in {"amd64", "x86_64"}:
        problems.append("PolyVoice requires 64-bit x64 Windows and Python.")
    if os.environ.get("PYTHONHOME") or os.environ.get("PYTHONPATH"):
        problems.append("PYTHONHOME/PYTHONPATH must be cleared for PolyVoice's Python process.")

    stdlib = Path(sysconfig.get_path("stdlib"))
    if not (stdlib / "encodings" / "__init__.py").is_file() or not encodings.__file__:
        problems.append("Python's standard-library encodings module is missing.")
    if not (stdlib / "venv").is_dir():
        problems.append("Python's standard-library venv module is missing.")
    if not hasattr(venv, "EnvBuilder"):
        problems.append("Python's venv module could not be initialized.")
    if require_venv:
        expected = (project_root / ".venv").resolve()
        if Path(sys.prefix).resolve() != expected or Path(sys.prefix).resolve() == Path(sys.base_prefix).resolve():
            problems.append("Python is not running from this project's .venv.")
        if not Path(sys.executable).is_file() or not Path(getattr(sys, "_base_executable", sys.executable)).is_file():
            problems.append("The virtual environment or its base Python executable is missing.")

    if not project_root.is_dir():
        problems.append("The PolyVoice project folder could not be found.")

    total_ram = _physical_memory()
    if total_ram is not None:
        print(f"Physical RAM: {total_ram / 1024**3:.1f} GB (8 GB or more is recommended).")
        if total_ram < RECOMMENDED_RAM_BYTES:
            print("Warning: this computer has less than the recommended 8 GB RAM; synthesis may be slow or memory-limited.")
    else:
        print("Physical RAM could not be queried; 8 GB or more is recommended.")

    if preflight and project_root.is_dir():
        free_bytes = shutil.disk_usage(project_root).free
        print(f"Free space on the project drive: {free_bytes / 1024**3:.1f} GB; at least 5 GB is required for setup.")
        if free_bytes < MINIMUM_FREE_BYTES:
            problems.append("At least 5 GB of free disk space is required before downloading packages and models.")

    for problem in problems:
        print(f"ERROR: {problem}", file=sys.stderr)
    if problems:
        return 1
    print(f"Python {sys.version.split()[0]} ({platform.machine()}) and standard-library checks passed.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--preflight", action="store_true", help="also enforce the 5 GB setup disk-space minimum")
    parser.add_argument("--venv", action="store_true", help="require this project's .venv")
    args = parser.parse_args()
    return check(args.project_root.resolve(), preflight=args.preflight, require_venv=args.venv)


if __name__ == "__main__":
    raise SystemExit(main())
