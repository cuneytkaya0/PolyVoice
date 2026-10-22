"""Download Kokoro's model and all advertised voice packs for offline use."""

from pathlib import Path
import os
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
TEMP_ROOT = ROOT / ".tmp"
TEMP_ROOT.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("TEMP", str(ROOT / ".tmp"))
os.environ.setdefault("TMP", str(ROOT / ".tmp"))
os.environ.setdefault("HF_HOME", str(ROOT / "models" / "hf-cache"))
os.environ.setdefault("HF_HUB_CACHE", str(ROOT / "models" / "hf-cache" / "hub"))
os.environ.pop("HF_HUB_OFFLINE", None)

from misaki import ja as misaki_ja
from misaki.ja import JAG2P as BaseJAG2P


class OfflineJAG2P(BaseJAG2P):
    def __init__(self, *args, **kwargs):
        super().__init__(version="pyopenjtalk")


misaki_ja.JAG2P = OfflineJAG2P

from kokoro import KPipeline
from kokoro.model import KModel

from polyvoice.catalog import VOICES


LANGUAGE_CODES = {"en-us": "a", "en-gb": "b", "ja": "j", "zh": "z"}
REPO_ID = "hexgrad/Kokoro-82M"


def main():
    print("Downloading the official Kokoro model and voice packs into this project's models folder.", flush=True)
    model = KModel(repo_id=REPO_ID).to("cpu").eval()
    for language, code in LANGUAGE_CODES.items():
        pipeline = KPipeline(lang_code=code, repo_id=REPO_ID, model=model, device="cpu")
        for voice in VOICES[language]:
            pipeline.load_voice(voice["id"])
        print(f"Cached {len(VOICES[language])} voices for {language}.", flush=True)
    print("Model and voice packs are ready for offline synthesis.", flush=True)


if __name__ == "__main__":
    main()
