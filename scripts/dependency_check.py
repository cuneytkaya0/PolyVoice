"""Check exact direct dependency versions and required runtime files."""

from __future__ import annotations

import importlib.metadata as metadata
import importlib.util
import json
from pathlib import Path
import sys


VERSIONS = {
    "Flask": "3.1.3",
    "torch": "2.14.1+cpu",
    "kokoro": "0.9.4",
    "misaki": "0.9.4",
    "phonemizer-fork": "3.3.2",
    "espeakng-loader": "0.2.4",
    "pyopenjtalk-plus": "0.4.1.post9",
    "numpy": "2.5.4",
    "soundfile": "0.14.0",
}
MODULES = (
    "flask", "torch", "kokoro", "misaki", "misaki.en", "misaki.ja",
    "misaki.zh", "misaki.de", "phonemizer", "espeakng_loader",
    "pyopenjtalk", "numpy", "soundfile", "spacy", "en_core_web_sm",
)
DIRECT_COMMITS = {
    "kokoro": "b96fef95e6a746495f92443fac7c688f90fc57fc",
    "misaki": "9cda9268309160120fffee216280a9ca83ac4644",
}


def check() -> list[str]:
    issues: list[str] = []
    if sys.version_info[:2] != (3, 12):
        issues.append(f"Python 3.12 required; found {sys.version.split()[0]}.")
    for package, expected in VERSIONS.items():
        try:
            actual = metadata.version(package)
        except metadata.PackageNotFoundError:
            issues.append(f"Missing package: {package}.")
            continue
        if actual != expected:
            issues.append(f"{package} version mismatch: expected {expected}, found {actual}.")
    for module in MODULES:
        try:
            found = importlib.util.find_spec(module) is not None
        except (ImportError, ModuleNotFoundError, ValueError):
            found = False
        if not found:
            issues.append(f"Missing import: {module}.")

    for package, expected_commit in DIRECT_COMMITS.items():
        try:
            direct = metadata.distribution(package).read_text("direct_url.json")
            origin = json.loads(direct or "{}")
            actual_commit = origin.get("vcs_info", {}).get("commit_id")
            url = origin.get("url", "").lower()
        except (metadata.PackageNotFoundError, json.JSONDecodeError, OSError):
            actual_commit = None
            url = ""
        if actual_commit != expected_commit and expected_commit not in url:
            issues.append(f"{package} is not installed from the pinned source commit.")

    try:
        import espeakng_loader

        loader_dir = Path(espeakng_loader.__file__).resolve().parent
        if not (loader_dir / "espeak-ng.dll").is_file():
            issues.append("The project-local eSpeak NG DLL is missing.")
        if not (loader_dir / "espeak-ng-data" / "de_dict").is_file():
            issues.append("The project-local eSpeak NG German dictionary is missing.")
    except (ImportError, OSError, TypeError):
        issues.append("The project-local eSpeak NG runtime could not be inspected.")

    return issues


def main() -> int:
    issues = check()
    if issues:
        for issue in issues:
            print(f"ERROR: {issue}", file=sys.stderr)
        return 1
    print("All pinned Python packages, language modules, and eSpeak NG files are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
