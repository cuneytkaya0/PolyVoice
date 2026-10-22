"""Run PolyVoice on the local machine only."""

import os
import socket
import logging
from pathlib import Path

project_root = Path(__file__).resolve().parent
os.environ["TEMP"] = str(project_root / ".tmp")
os.environ["TMP"] = str(project_root / ".tmp")
os.environ.setdefault("HF_HOME", str(project_root / "models" / "hf-cache"))
os.environ.setdefault("HF_HUB_CACHE", str(project_root / "models" / "hf-cache" / "hub"))

from polyvoice import create_app
from polyvoice.engine import EngineUnavailableError

app = create_app()


if __name__ == "__main__":
    logging.getLogger("werkzeug").setLevel(logging.ERROR)
    try:
        app.extensions["tts_engine"].prepare()
    except EngineUnavailableError as exc:
        print(f"PolyVoice setup issue: {exc}")
        raise SystemExit(1) from exc
    preferred_port = int(os.environ.get("POLYVOICE_PORT", "5000"))
    port = None
    for candidate in [preferred_port, *range(preferred_port + 1, preferred_port + 101)]:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            try:
                probe.bind(("127.0.0.1", candidate))
            except OSError:
                continue
            port = candidate
            break
    if port is None:
        raise SystemExit("No free localhost port was found in the configured range.")
    print(f"PolyVoice is running at http://127.0.0.1:{port}", flush=True)
    app.run(host="127.0.0.1", port=port, debug=False, threaded=False)
