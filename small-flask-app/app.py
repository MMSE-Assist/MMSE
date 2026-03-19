import base64
from dataclasses import dataclass, field
from datetime import datetime, timezone
from io import BytesIO
from threading import Lock

from flask import Flask, jsonify, render_template, request, send_file


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_image(image_value: str) -> str:
    image_value = image_value.strip()
    if not image_value:
        raise ValueError("Image payload is empty.")
    if image_value.startswith("data:image/"):
        return image_value
    return f"data:image/png;base64,{image_value}"


def _decode_data_url(data_url: str) -> tuple[str, bytes]:
    header, encoded = data_url.split(",", 1)
    mime_type = header.split(";", 1)[0].removeprefix("data:")
    return mime_type or "image/png", base64.b64decode(encoded)


@dataclass
class DrawingState:
    prompt_image: str | None = None
    drawing_image: str | None = None
    drawing_done: bool = False
    version: int = 0
    updated_at: str = field(default_factory=_utc_now)


class DrawingStore:
    def __init__(self) -> None:
        self._state = DrawingState()
        self._lock = Lock()

    def set_prompt_image(self, image_value: str) -> DrawingState:
        normalized = _normalize_image(image_value)
        with self._lock:
            self._state.prompt_image = normalized
            self._state.drawing_image = None
            self._state.drawing_done = False
            self._state.version += 1
            self._state.updated_at = _utc_now()
            return DrawingState(**self._state.__dict__)

    def save_drawing(self, image_value: str, done: bool) -> DrawingState:
        normalized = _normalize_image(image_value)
        with self._lock:
            self._state.drawing_image = normalized
            self._state.drawing_done = done
            self._state.updated_at = _utc_now()
            return DrawingState(**self._state.__dict__)

    def consume_drawing(self) -> DrawingState:
        """Return the current state and immediately clear it so the UI resets."""
        with self._lock:
            snapshot = DrawingState(**self._state.__dict__)
            self._state.prompt_image = None
            self._state.drawing_image = None
            self._state.drawing_done = False
            self._state.version += 1
            self._state.updated_at = _utc_now()
            return snapshot

    def get_state(self) -> DrawingState:
        with self._lock:
            return DrawingState(**self._state.__dict__)


app = Flask(__name__)
store = DrawingStore()


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/draw")
def set_reference_image():
    payload = request.get_json(silent=True) or {}
    image_value = (
        payload.get("image") or request.form.get("image") or request.values.get("image")
    )
    if not image_value:
        return jsonify({"error": "Missing 'image' field."}), 400

    try:
        state = store.set_prompt_image(image_value)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(
        {
            "status": "ok",
            "message": "Reference image updated.",
            "version": state.version,
            "updatedAt": state.updated_at,
        }
    )


@app.get("/draw")
def get_finished_drawing():
    state = store.get_state()
    if not state.drawing_image or not state.drawing_done:
        return jsonify({"error": "No completed drawing available yet."}), 404

    # Consume the drawing: clears store so the UI resets on next poll.
    store.consume_drawing()

    mime_type, image_bytes = _decode_data_url(state.drawing_image)
    return send_file(
        BytesIO(image_bytes),
        mimetype=mime_type,
        as_attachment=False,
        download_name="user_drawing.png",
    )


@app.get("/api/state")
def get_state():
    state = store.get_state()
    return jsonify(
        {
            "promptImage": state.prompt_image,
            "drawingReady": state.drawing_done,
            "hasDrawing": state.drawing_image is not None,
            "version": state.version,
            "updatedAt": state.updated_at,
        }
    )


@app.post("/api/drawing")
def save_drawing():
    payload = request.get_json(silent=True) or {}
    image_value = payload.get("image")
    if not image_value:
        return jsonify({"error": "Missing 'image' field."}), 400

    try:
        state = store.save_drawing(image_value, bool(payload.get("done", False)))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(
        {
            "status": "ok",
            "drawingReady": state.drawing_done,
            "updatedAt": state.updated_at,
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
