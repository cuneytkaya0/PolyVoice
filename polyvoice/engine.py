"""Offline Kokoro inference and temporary audio lifecycle."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import os
import secrets
import re
import threading
import time
import gc

import numpy as np
import soundfile as sf
import torch

from .catalog import VOICES


PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_CACHE = PROJECT_ROOT / "models" / "hf-cache"
OUTPUT_ROOT = PROJECT_ROOT / "outputs"
TEMP_ROOT = OUTPUT_ROOT / "temporary"
PREVIEW_ROOT = OUTPUT_ROOT / "previews"
REPO_ID = "hexgrad/Kokoro-82M"
SAMPLE_RATE = 24_000
JAPANESE_MAX_PHONEMES = 450
LANGUAGE_CODES = {"en-us": "a", "en-gb": "b", "ja": "j", "zh": "z"}
GERMAN_MODEL_DIR = PROJECT_ROOT / "models" / "kikiri-german-martin"
GERMAN_CHECKPOINT = GERMAN_MODEL_DIR / "kikiri_german_martin_ep10.pth"
GERMAN_VOICEPACK = GERMAN_MODEL_DIR / "voices" / "martin.pt"
GERMAN_VICTORIA_DIR = PROJECT_ROOT / "models" / "kikiri-german-victoria"
GERMAN_VICTORIA_CHECKPOINT = GERMAN_VICTORIA_DIR / "kikiri_german_victoria_ep10.pth"
GERMAN_VICTORIA_VOICEPACK = GERMAN_VICTORIA_DIR / "voices" / "victoria.pt"
VICTORIA_ASSETS = (
    (GERMAN_VICTORIA_CHECKPOINT, 327_231_582, "128d1c4a4184a459f23cb307a6cbbb8e9c076c2526f86e18594c1b320a81e00c"),
    (GERMAN_VICTORIA_VOICEPACK, 523_445, "18dbcf0afa7b737e450e6ba769ee898a5aae1d90218265ff4c95422f4693da50"),
)
PREVIEW_TEXT = {
    "en-us": "Hello there. This is your voice preview.",
    "en-gb": "Hello there. This is your voice preview.",
    "ja": "こんにちは。音声です。",
    "zh": "你好，试听一下。",
    "de": "Guten Tag. Dies ist eine Hörprobe.",
}
TEMP_TTL_SECONDS = 60 * 60


def _split_japanese_text(text, g2p, max_phonemes=JAPANESE_MAX_PHONEMES):
    """Split Japanese before Kokoro's 510-character phoneme truncation point."""
    sentences = [part for part in re.split(r"(?<=[。！？!?])", text) if part]
    if not sentences:
        return [text]

    output = []
    current = ""

    def phoneme_length(value):
        return len(g2p(value)[0])

    for sentence in sentences:
        candidate = current + sentence
        if phoneme_length(candidate) <= max_phonemes:
            current = candidate
            continue

        if current:
            output.append(current)
            current = ""

        if phoneme_length(sentence) <= max_phonemes:
            current = sentence
            continue

        # A single long sentence has no safe punctuation boundary. Misaki's
        # Japanese tokens retain source surfaces and are safer split points
        # than arbitrary Unicode character offsets.
        _phonemes, tokens = g2p(sentence)
        if not tokens:
            raise EngineUnavailableError("This Japanese sentence is too long to split safely.")
        for token in tokens:
            token_text = token.text + token.whitespace
            candidate = current + token_text
            if phoneme_length(candidate) <= max_phonemes:
                current = candidate
                continue
            if current:
                output.append(current)
            if phoneme_length(token_text) > max_phonemes:
                raise EngineUnavailableError("A Japanese word exceeds the safe speech chunk size.")
            current = token_text

    if current:
        output.append(current)
    return output


def _suppress_japanese_neutral_pitch_tokens(g2p):
    """Keep Misaki's Japanese phones but neutralize its colliding pitch marker.

    Misaki appends a second, character-aligned pitch track to Japanese G2P
    output. In this track, ``j`` means "no pitch mark"; Kokoro 0.9.4's
    vocabulary maps ``j`` to a real /j/ speech token while ignoring the other
    pitch symbols. That accidentally feeds the no-pitch placeholders to the
    speech model as consonants. Replace only those markers in the second half
    with ``_``, which Kokoro already ignores, keeping both tracks aligned.
    """
    def adapted(text):
        phonemes, tokens = g2p(text)
        if len(phonemes) % 2:
            return phonemes, tokens
        midpoint = len(phonemes) // 2
        phone_track, pitch_track = phonemes[:midpoint], phonemes[midpoint:]
        return phone_track + pitch_track.replace("j", "_"), tokens

    return adapted


class EngineUnavailableError(RuntimeError):
    """Raised when synthesis is requested before the local engine is ready."""


@dataclass(frozen=True)
class AudioAsset:
    path: Path
    expires_at: float


class SynthesisEngine:
    """One CPU Kokoro model shared across language-specific pipelines."""

    def __init__(self):
        self._lock = threading.Lock()
        self._model = None
        self._german_model = None
        self._german_voice = None
        self._victoria_validation = None
        self._pipelines = {}
        self._assets: dict[str, AudioAsset] = {}
        self._prepared = False
        self._prepare_error = None
        self.status_message = "Loading local Kokoro models and voices…"
        TEMP_ROOT.mkdir(parents=True, exist_ok=True)
        PREVIEW_ROOT.mkdir(parents=True, exist_ok=True)
        self._remove_expired_files()

    @property
    def available(self):
        return self._prepared

    def prepare(self):
        """Load local weights and every advertised voice pack with Hub offline mode."""
        with self._lock:
            if self._prepared:
                return
            if self._prepare_error:
                raise EngineUnavailableError(self.status_message)
            try:
                os.environ.setdefault("HF_HOME", str(MODEL_CACHE))
                os.environ.setdefault("HF_HUB_CACHE", str(MODEL_CACHE / "hub"))
                os.environ["HF_HUB_OFFLINE"] = "1"

                # Misaki's default Japanese G2P uses Cutlet/UniDic. Kokoro's
                # pyopenjtalk path is also supported and pyopenjtalk-plus
                # bundles its Japanese dictionary in a CPython 3.12 Windows wheel.
                from misaki import ja as misaki_ja
                from misaki.ja import JAG2P as BaseJAG2P

                class OfflineJAG2P(BaseJAG2P):
                    def __init__(self, *args, **kwargs):
                        super().__init__(version="pyopenjtalk")

                misaki_ja.JAG2P = OfflineJAG2P

                from kokoro import KPipeline
                from kokoro.model import KModel

                self._model = KModel(repo_id=REPO_ID).to("cpu").eval()
                for language, code in LANGUAGE_CODES.items():
                    pipeline = KPipeline(
                        lang_code=code,
                        repo_id=REPO_ID,
                        model=self._model,
                        device="cpu",
                    )
                    if language == "ja":
                        pipeline.g2p = _suppress_japanese_neutral_pitch_tokens(pipeline.g2p)
                    # Force each available embedding to be resolved from the
                    # local cache now; later requests never need network access.
                    for voice in VOICES[language]:
                        pipeline.load_voice(voice["id"])
                    self._pipelines[language] = pipeline
                if not GERMAN_CHECKPOINT.is_file() or not GERMAN_VOICEPACK.is_file():
                    raise EngineUnavailableError(
                        "Kikiri German Martin files are missing. Run setup.bat while online, then restart PolyVoice."
                    )
                self._german_model_class = KModel
                self._german_pipeline_class = KPipeline
                self._pipelines["de"] = True
                self._prepared = True
                self.status_message = "Ready. Speech is generated locally on your CPU."
            except Exception as exc:
                self._prepare_error = exc
                self.status_message = (
                    "Local speech models are incomplete or could not be loaded. "
                    "Run setup.bat with an internet connection, then restart PolyVoice."
                )
                raise EngineUnavailableError(self.status_message) from exc

    def available_voices(self):
        """Return only German voices whose pinned local assets are present."""
        available = {key: list(value) for key, value in VOICES.items()}
        if not self._victoria_assets_verified():
            available["de"] = [voice for voice in available["de"] if voice["id"] != "victoria"]
        return available

    def _victoria_assets_verified(self):
        signatures = []
        try:
            for path, expected_size, _expected_hash in VICTORIA_ASSETS:
                info = path.stat()
                signatures.append((info.st_size, info.st_mtime_ns))
        except OSError:
            self._victoria_validation = None
            return False
        signature = tuple(signatures)
        if self._victoria_validation and self._victoria_validation[0] == signature:
            return self._victoria_validation[1]
        verified = True
        for path, expected_size, expected_hash in VICTORIA_ASSETS:
            if path.stat().st_size != expected_size or self._sha256(path) != expected_hash:
                verified = False
                break
        self._victoria_validation = (signature, verified)
        return verified

    @staticmethod
    def _sha256(path):
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
        return digest.hexdigest()

    def generate(self, *, text, language, voice, speed):
        return self._synthesize(text, language, voice, speed)

    def preview(self, *, language, voice):
        cache_path = PREVIEW_ROOT / f"{language}-{voice}.wav"
        with self._lock:
            self._require_prepared()
            if not cache_path.is_file():
                self._write_speech(PREVIEW_TEXT[language], language, voice, 1.0, cache_path)
            asset_id = self._register_asset(cache_path)
            return {"audio_url": f"/api/audio/{asset_id}", "duration": round(sf.info(cache_path).duration, 3)}

    def _synthesize(self, text, language, voice, speed):
        with self._lock:
            self._require_prepared()
            destination = TEMP_ROOT / f"{secrets.token_hex(16)}.wav"
            try:
                duration = self._write_speech(text, language, voice, speed, destination)
            except Exception:
                destination.unlink(missing_ok=True)
                raise
            asset_id = self._register_asset(destination)
            return {
                "audio_url": f"/api/audio/{asset_id}",
                "download_url": f"/api/audio/{asset_id}?download=1",
                "duration": duration,
                "sample_rate": SAMPLE_RATE,
            }

    def _write_speech(self, text, language, voice, speed, destination):
        pipeline = self._get_pipeline(language, voice)
        if pipeline is None or voice not in {item["id"] for item in self.available_voices().get(language, [])}:
            raise EngineUnavailableError("That language or voice is not available.")
        chunks = []
        voice_arg = str(GERMAN_VOICEPACK if voice == "martin" else GERMAN_VICTORIA_VOICEPACK) if language == "de" else voice
        # Kokoro 0.9.4's non-English path recognizes only ASCII sentence stops
        # and truncates any resulting phoneme string over 510 characters. Its
        # Japanese path therefore silently cuts ordinary long paragraphs at
        # an arbitrary phoneme boundary. Split Japanese at native sentence
        # boundaries, then use Misaki tokens as a safe fallback for long
        # unpunctuated sentences. Keep a margin below Kokoro's hard limit.
        input_segments = _split_japanese_text(text, pipeline.g2p) if language == "ja" else text
        with torch.inference_mode():
            for result in pipeline(input_segments, voice=voice_arg, speed=speed):
                if result.audio is not None:
                    audio = result.audio.detach().to("cpu").numpy().reshape(-1)
                    if audio.size:
                        chunks.append(audio)
        if not chunks:
            raise EngineUnavailableError("No speech audio was produced for this text.")
        waveform = np.concatenate(chunks).astype(np.float32, copy=False)
        if not np.isfinite(waveform).all() or not np.max(np.abs(waveform)) > 1e-5:
            raise EngineUnavailableError("The speech engine returned invalid audio.")
        sf.write(destination, waveform, SAMPLE_RATE, subtype="PCM_16", format="WAV")
        return round(len(waveform) / SAMPLE_RATE, 3)

    def _get_pipeline(self, language, voice):
        if language != "de":
            return self._pipelines.get(language)
        if voice not in {item["id"] for item in self.available_voices().get("de", [])}:
            return None
        if self._german_voice == voice:
            return self._pipelines.get("de")
        # Keep only one ~327 MB German checkpoint resident at a time.
        self._pipelines.pop("de", None)
        self._german_model = None
        gc.collect()
        checkpoint = GERMAN_CHECKPOINT if voice == "martin" else GERMAN_VICTORIA_CHECKPOINT
        self._german_model = self._german_model_class(repo_id=REPO_ID, model=str(checkpoint)).to("cpu").eval()
        self._pipelines["de"] = self._german_pipeline_class(
            lang_code="de", repo_id=REPO_ID, model=self._german_model, device="cpu"
        )
        self._german_voice = voice
        return self._pipelines["de"]

    def _register_asset(self, path):
        self._cleanup_assets()
        asset_id = secrets.token_urlsafe(24)
        self._assets[asset_id] = AudioAsset(path=path, expires_at=time.monotonic() + TEMP_TTL_SECONDS)
        self._latest_asset_id = asset_id
        return asset_id

    def resolve_audio(self, asset_id):
        self._cleanup_assets()
        asset = self._assets.get(asset_id)
        return asset.path if asset and asset.path.is_file() else None

    def _require_prepared(self):
        if not self._prepared:
            raise EngineUnavailableError(self.status_message)

    def _cleanup_assets(self):
        now = time.monotonic()
        for asset_id, asset in list(self._assets.items()):
            if asset.expires_at <= now:
                if asset.path.parent == TEMP_ROOT:
                    asset.path.unlink(missing_ok=True)
                del self._assets[asset_id]

    @staticmethod
    def _remove_expired_files():
        cutoff = time.time() - TEMP_TTL_SECONDS
        for path in TEMP_ROOT.glob("*.wav"):
            try:
                if path.stat().st_mtime < cutoff:
                    path.unlink(missing_ok=True)
            except OSError:
                continue
