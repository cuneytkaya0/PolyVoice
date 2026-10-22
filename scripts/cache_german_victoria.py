"""Download and verify the approved Kikiri German Victoria assets."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "models" / "kikiri-german-victoria"
REPO = "kikiri-tts/kikiri-german-victoria"
ASSETS = (
    (
        "kikiri_german_victoria_ep10.pth",
        "kikiri_german_victoria_ep10.pth",
        "ce81e200ff9203e1a3b042cd678c48e3ffb85cef",
        327_231_582,
        "128d1c4a4184a459f23cb307a6cbbb8e9c076c2526f86e18594c1b320a81e00c",
    ),
    (
        "voices/victoria.pt",
        "voices/victoria.pt",
        "9f71f85f8e7b4b18bdd691d4e4f3bbc605abc9e2",
        523_445,
        "18dbcf0afa7b737e450e6ba769ee898a5aae1d90218265ff4c95422f4693da50",
    ),
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    os.environ.setdefault("TEMP", str(ROOT / ".tmp"))
    os.environ.setdefault("TMP", str(ROOT / ".tmp"))
    os.environ.setdefault("HF_HOME", str(ROOT / "models" / "hf-cache"))
    from huggingface_hub import hf_hub_download

    for filename, relative, revision, expected_size, expected_hash in ASSETS:
        destination = TARGET / relative
        if destination.is_file() and destination.stat().st_size == expected_size and sha256(destination) == expected_hash:
            print(f"Verified existing {filename}.", flush=True)
            continue
        print(f"Downloading {filename} ({expected_size / 1_000_000:.1f} MB) from its pinned revision…", flush=True)
        downloaded = Path(hf_hub_download(
            repo_id=REPO,
            filename=filename,
            revision=revision,
            local_dir=TARGET,
        ))
        if downloaded.stat().st_size != expected_size or sha256(downloaded) != expected_hash:
            raise RuntimeError(f"Checksum or size verification failed for {filename}; do not use this file.")
        print(f"Verified {filename} (SHA-256 {expected_hash}).", flush=True)
    print("Kikiri German Victoria is ready for local offline use.", flush=True)


if __name__ == "__main__":
    main()
