"""Cache the approved Kikiri German Martin checkpoint and voice pack locally."""

from pathlib import Path
import hashlib
import os

ROOT = Path(__file__).resolve().parents[1]
os.environ["TEMP"] = str(ROOT / ".tmp")
os.environ["TMP"] = str(ROOT / ".tmp")
os.environ.setdefault("HF_HOME", str(ROOT / "models" / "hf-cache"))

from huggingface_hub import hf_hub_download


def main():
    target = ROOT / "models" / "kikiri-german-martin"
    target.mkdir(parents=True, exist_ok=True)
    checkpoint = hf_hub_download(
        repo_id="kikiri-tts/kikiri-german-martin",
        filename="kikiri_german_martin_ep10.pth",
        local_dir=target,
    )
    voicepack = hf_hub_download(
        repo_id="kikiri-tts/kikiri-german-martin",
        filename="voices/martin.pt",
        local_dir=target,
    )
    if Path(checkpoint).stat().st_size < 300_000_000 or Path(voicepack).stat().st_size < 100_000:
        raise RuntimeError("The downloaded Kikiri Martin files failed their size checks.")
    digestor = hashlib.sha256()
    with Path(checkpoint).open("rb") as model_file:
        for block in iter(lambda: model_file.read(1024 * 1024), b""):
            digestor.update(block)
    digest = digestor.hexdigest()
    if digest != "f194905cc97d4ef16e0f2613c2d277203e0c0f0f533e0a468c7ec76c566259dc":
        raise RuntimeError("The Kikiri Martin checkpoint checksum does not match the reviewed model file.")
    print("Kikiri German Martin model and voice pack are ready for offline use.")


if __name__ == "__main__":
    main()
