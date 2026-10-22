"""PolyVoice local text-to-speech application."""

from flask import Flask, jsonify, render_template, request, send_file
from pathlib import Path

from .catalog import LANGUAGES, MAX_TEXT_LENGTH, VOICES
from .engine import EngineUnavailableError, SynthesisEngine


def create_app(engine=None):
    project_root = Path(__file__).resolve().parent.parent
    app = Flask(
        __name__,
        template_folder=str(project_root / "templates"),
        static_folder=str(project_root / "static"),
    )
    app.config.update(
        MAX_CONTENT_LENGTH=128 * 1024,
        MAX_TEXT_LENGTH=MAX_TEXT_LENGTH,
        JSON_AS_ASCII=False,
    )
    app.extensions["tts_engine"] = engine or SynthesisEngine()

    @app.after_request
    def add_security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        response.headers.setdefault("Content-Security-Policy", "default-src 'self'; media-src 'self' blob:; style-src 'self'; script-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; frame-ancestors 'none'")
        return response

    @app.get("/")
    def index():
        return render_template("index.html", max_text_length=MAX_TEXT_LENGTH)

    @app.get("/api/config")
    def config():
        engine_instance = app.extensions["tts_engine"]
        voices = engine_instance.available_voices() if hasattr(engine_instance, "available_voices") else VOICES
        return jsonify({
            "languages": LANGUAGES,
            "voices": voices,
            "max_text_length": MAX_TEXT_LENGTH,
            "synthesis_available": engine_instance.available,
            "preview_available": engine_instance.available,
            "status_message": engine_instance.status_message,
        })

    @app.get("/api/health")
    def health():
        engine_instance = app.extensions["tts_engine"]
        return jsonify({"status": "ok", "synthesis_available": engine_instance.available})

    @app.post("/api/generate")
    def generate():
        payload = _json_payload()
        if isinstance(payload, tuple):
            return payload
        text = payload.get("text", "")
        if not isinstance(text, str) or not text.strip():
            return jsonify(error="Enter some text before generating audio."), 400
        if len(text) > MAX_TEXT_LENGTH:
            return jsonify(error=f"Text must be {MAX_TEXT_LENGTH:,} characters or fewer."), 413
        language = payload.get("language")
        voice_id = payload.get("voice")
        voice = _find_voice(language, voice_id)
        if voice is None or not voice["enabled"]:
            return jsonify(error="That language or voice is not available yet."), 400
        try:
            speed = float(payload.get("speed", 1.0))
        except (TypeError, ValueError):
            return jsonify(error="Speed must be a number from 0.5x to 1.5x."), 400
        if not 0.5 <= speed <= 1.5:
            return jsonify(error="Speed must be between 0.5x and 1.5x."), 400
        try:
            result = app.extensions["tts_engine"].generate(text=text, language=language, voice=voice_id, speed=speed)
        except EngineUnavailableError as exc:
            return jsonify(error=str(exc)), 503
        except Exception:
            return jsonify(error="Speech could not be generated. Try a shorter text or check the local model setup."), 500
        return jsonify(result)

    @app.post("/api/preview")
    def preview():
        payload = _json_payload()
        if isinstance(payload, tuple):
            return payload
        voice = _find_voice(payload.get("language"), payload.get("voice"))
        if voice is None or not voice["enabled"]:
            return jsonify(error="That voice is not available yet."), 400
        try:
            result = app.extensions["tts_engine"].preview(language=payload["language"], voice=voice["id"])
        except EngineUnavailableError as exc:
            return jsonify(error=str(exc)), 503
        except Exception:
            return jsonify(error="This voice preview could not be created. Restart PolyVoice and try again."), 500
        return jsonify(result)

    @app.get("/api/audio/<asset_id>")
    def audio(asset_id):
        path = app.extensions["tts_engine"].resolve_audio(asset_id)
        if path is None:
            return jsonify(error="This temporary audio has expired. Generate it again."), 404
        return send_file(
            path,
            mimetype="audio/wav",
            as_attachment=request.args.get("download") == "1",
            download_name="polyvoice-audio.wav",
            conditional=True,
            max_age=0,
        )

    @app.errorhandler(413)
    def request_too_large(_error):
        return jsonify(error="This request is too large."), 413

    return app


def _json_payload():
    from flask import request

    if not request.is_json:
        return jsonify(error="Send a JSON request."), 415
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify(error="The request body must be a JSON object."), 400
    return payload


def _find_voice(language, voice_id):
    if not isinstance(language, str) or not isinstance(voice_id, str):
        return None
    for voice in VOICES.get(language, []):
        if voice["id"] == voice_id:
            return voice
    return None
