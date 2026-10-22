import unittest

from polyvoice import create_app
from polyvoice.engine import _split_japanese_text, _suppress_japanese_neutral_pitch_tokens
from misaki.ja import JAG2P


class FakeEngine:
    available = True
    status_message = "ready"

    def generate(self, **kwargs):
        return {"audio_url": "/api/audio/fake", "download_url": "/api/audio/fake?download=1", "duration": 1.0}

    def preview(self, **kwargs):
        return {"audio_url": "/api/audio/fake", "duration": 2.0}

    def resolve_audio(self, asset_id):
        return None


class AppApiTests(unittest.TestCase):
    def setUp(self):
        self.client = create_app(FakeEngine()).test_client()

    def test_homepage_has_editor_and_player(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"text-input", response.data)
        self.assertIn(b"player-section", response.data)
        self.assertNotIn(b"WORD TRACKING", response.data)
        self.assertNotIn(b"Dictionary", response.data)

    def test_config_lists_english_variants_and_three_other_languages(self):
        response = self.client.get("/api/config")
        self.assertEqual(response.status_code, 200)
        config = response.get_json()
        self.assertEqual({item["id"] for item in config["languages"] if item["enabled"]}, {"en-us", "en-gb", "de", "ja", "zh"})
        self.assertNotIn("word_tracking_available", config)


    def test_empty_text_is_rejected(self):
        response = self.client.post("/api/generate", json={"text": " ", "language": "en-us", "voice": "af_heart"})
        self.assertEqual(response.status_code, 400)

    def test_invalid_speed_is_rejected(self):
        response = self.client.post("/api/generate", json={"text": "Hello", "language": "en-us", "voice": "af_heart", "speed": 2})
        self.assertEqual(response.status_code, 400)

    def test_speed_boundaries_are_accepted(self):
        for speed in (0.5, 1.5):
            with self.subTest(speed=speed):
                response = self.client.post("/api/generate", json={
                    "text": "Hello", "language": "en-us", "voice": "af_heart", "speed": speed,
                })
                self.assertEqual(response.status_code, 200)

    def test_unknown_voice_is_rejected(self):
        response = self.client.post("/api/generate", json={
            "text": "Hello", "language": "de", "voice": "not-a-voice", "speed": 1,
        })
        self.assertEqual(response.status_code, 400)

    def test_non_json_request_is_rejected(self):
        response = self.client.post("/api/generate", data="hello", content_type="text/plain")
        self.assertEqual(response.status_code, 415)

    def test_malformed_json_is_rejected(self):
        response = self.client.post("/api/generate", data="{bad", content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_overlong_text_is_rejected(self):
        response = self.client.post("/api/generate", json={
            "text": "a" * 10_001, "language": "en-us", "voice": "af_heart",
        })
        self.assertEqual(response.status_code, 413)

    def test_preview_returns_local_audio_endpoint(self):
        response = self.client.post("/api/preview", json={"language": "en-us", "voice": "af_heart"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()["audio_url"].startswith("/api/audio/"))

    def test_invalid_preview_language_type_is_rejected(self):
        response = self.client.post("/api/preview", json={"language": ["en-us"], "voice": "af_heart"})
        self.assertEqual(response.status_code, 400)

    def test_config_exposes_supported_voice_catalog(self):
        config = self.client.get("/api/config").get_json()
        self.assertIn("martin", {voice["id"] for voice in config["voices"]["de"]})
        self.assertNotIn("word_tracking_available", config)


class JapaneseSegmentationTests(unittest.TestCase):
    def test_long_japanese_paragraph_is_split_without_losing_misaki_tokens(self):
        g2p = JAG2P(version="pyopenjtalk")
        sentence = "今日はいい天気です。公園を散歩します。鳥の声が聞こえます。風が気持ちいいです。"
        text = sentence * 8

        segments = _split_japanese_text(text, g2p)

        self.assertGreater(len(segments), 1)
        self.assertEqual("".join(segments), text)
        self.assertTrue(all(len(g2p(segment)[0]) <= 450 for segment in segments))

    def test_short_japanese_and_terminal_punctuation_are_preserved(self):
        g2p = JAG2P(version="pyopenjtalk")
        for text in ("こんにちは。", "こんにちは", "今日はいい天気です！"):
            with self.subTest(text=text):
                self.assertEqual(_split_japanese_text(text, g2p), [text])

    def test_neutral_pitch_marker_is_removed_without_changing_phone_track_or_text(self):
        g2p = JAG2P(version="pyopenjtalk")
        text = "散歩をしたり、本を読んだりするのも好きです。"
        phonemes, tokens = g2p(text)
        midpoint = len(phonemes) // 2
        adapted_phonemes, adapted_tokens = _suppress_japanese_neutral_pitch_tokens(g2p)(text)

        self.assertEqual(adapted_phonemes[:midpoint], phonemes[:midpoint])
        self.assertEqual(len(adapted_phonemes), len(phonemes))
        self.assertNotIn("j", adapted_phonemes[midpoint:])
        self.assertEqual([token.text for token in adapted_tokens], [token.text for token in tokens])

    def test_long_unpunctuated_sentence_splits_at_misaki_tokens(self):
        g2p = JAG2P(version="pyopenjtalk")
        text = "今日はいい天気です 公園を散歩します 鳥の声が聞こえます 風が気持ちいいです " * 8
        _phonemes, tokens = g2p(text)
        expected_surfaces = "".join(token.text + token.whitespace for token in tokens)

        segments = _split_japanese_text(text, g2p)

        self.assertGreater(len(segments), 1)
        self.assertEqual("".join(segments), expected_surfaces)
        self.assertTrue(all(len(g2p(segment)[0]) <= 450 for segment in segments))


if __name__ == "__main__":
    unittest.main()
