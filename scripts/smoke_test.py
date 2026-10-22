"""Generate and validate one CPU WAV per advertised language/locale."""

from pathlib import Path
from io import BytesIO
import os
import sys
import soundfile as sf

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["TEMP"] = str(ROOT / ".tmp")
os.environ["TMP"] = str(ROOT / ".tmp")
os.environ["HF_HOME"] = str(ROOT / "models" / "hf-cache")
os.environ["HF_HUB_CACHE"] = str(ROOT / "models" / "hf-cache" / "hub")

from polyvoice.catalog import VOICES
from polyvoice.engine import SynthesisEngine
from polyvoice import create_app


SAMPLES = {
    "en-us": "This is an American English test.",
    "en-gb": "This is a British English test.",
    "de": "Guten Tag. Dies ist ein deutscher Funktionstest.",
    "ja": "これは日本語の音声テストです。",
    "zh": "这是一段普通话语音测试。",
}


def main():
    engine = SynthesisEngine()
    engine.prepare()
    client = create_app(engine).test_client()
    results = []
    preview_results = []
    for language, text in SAMPLES.items():
      language_voices = engine.available_voices()[language]
      for voice_item in language_voices if language == "de" else language_voices[:1]:
        voice = voice_item["id"]
        response = client.post("/api/generate", json={"text": text, "language": language, "voice": voice, "speed": 1.0})
        if response.status_code != 200:
            raise AssertionError(f"Generate endpoint failed for {language}: {response.get_json()}")
        result = response.get_json()
        audio_response = client.get(result["download_url"])
        if audio_response.status_code != 200 or audio_response.mimetype != "audio/wav":
            raise AssertionError(f"WAV download endpoint failed for {language}")
        info = sf.info(BytesIO(audio_response.data))
        audio_response.close()
        if info.format != "WAV" or info.samplerate != 24_000 or info.frames <= 0:
            raise AssertionError(f"Invalid WAV for {language}: {info}")
        asset_id = result["audio_url"].rsplit("/", 1)[-1]
        results.append((language, voice, info.duration, engine.resolve_audio(asset_id)))
        preview_response = client.post("/api/preview", json={"language": language, "voice": voice})
        if preview_response.status_code != 200:
            raise AssertionError(f"Preview endpoint failed for {language}: {preview_response.get_json()}")
        preview = preview_response.get_json()
        preview_file = client.get(preview["audio_url"])
        preview_info = sf.info(BytesIO(preview_file.data))
        preview_file.close()
        if preview_info.format != "WAV" or preview_info.samplerate != 24_000 or not 1.0 <= preview_info.duration <= 6.0:
            raise AssertionError(f"Invalid preview for {language}: {preview_info}")
        preview_results.append((language, voice, preview_info.duration))

    durations = []
    for speed in (0.7, 1.3):
        response = client.post("/api/generate", json={"text": SAMPLES["en-us"], "language": "en-us", "voice": "af_heart", "speed": speed})
        if response.status_code != 200:
            raise AssertionError(f"Speed {speed}x failed: {response.get_json()}")
        result = response.get_json()
        durations.append((speed, result["duration"]))
        engine.resolve_audio(result["audio_url"].rsplit("/", 1)[-1]).unlink(missing_ok=True)
    if durations[0][1] <= durations[1][1]:
        raise AssertionError(f"Speed slider did not affect speech duration: {durations}")

    german_durations = {}
    for german_voice in (voice["id"] for voice in engine.available_voices()["de"]):
      voice_durations = []
      for speed in (0.7, 1.3):
        response = client.post("/api/generate", json={"text": SAMPLES["de"], "language": "de", "voice": german_voice, "speed": speed})
        if response.status_code != 200:
            raise AssertionError(f"German speed {speed}x for {german_voice} failed: {response.get_json()}")
        result = response.get_json()
        voice_durations.append((speed, result["duration"]))
        engine.resolve_audio(result["audio_url"].rsplit("/", 1)[-1]).unlink(missing_ok=True)
      if voice_durations[0][1] <= voice_durations[1][1]:
        raise AssertionError(f"German speed control did not change duration for {german_voice}: {voice_durations}")
      german_durations[german_voice] = voice_durations

    long_text = "Guten Tag. Dies ist ein deutscher Langtext-Test für PolyVoice. " * 12
    response = client.post("/api/generate", json={"text": long_text, "language": "de", "voice": "martin", "speed": 1.0})
    if response.status_code != 200 or response.get_json()["duration"] <= 10:
        raise AssertionError(f"German long-text synthesis failed: {response.get_json()}")
    engine.resolve_audio(response.get_json()["audio_url"].rsplit("/", 1)[-1]).unlink(missing_ok=True)

    for language, voice, duration, path in results:
        print(f"{language} / {voice}: WAV {duration:.2f}s, 24 kHz")
        path.unlink(missing_ok=True)
    for language, voice, duration in preview_results:
        print(f"preview {language} / {voice}: {duration:.2f}s")
    print(f"speed control: 0.7x={durations[0][1]:.2f}s, 1.3x={durations[1][1]:.2f}s")
    for voice, values in german_durations.items():
        print(f"German {voice} speed control: 0.7x={values[0][1]:.2f}s, 1.3x={values[1][1]:.2f}s")
    print(f"German long text: {len(long_text)} characters, {response.get_json()['duration']:.2f}s")


if __name__ == "__main__":
    main()
